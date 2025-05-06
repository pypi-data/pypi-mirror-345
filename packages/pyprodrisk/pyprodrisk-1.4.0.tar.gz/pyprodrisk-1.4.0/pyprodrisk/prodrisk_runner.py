import os
import sys
import platform
import pandas as pd
import numpy as np
import re
import datetime as dt

from .prodrisk_core.model_builder import ModelBuilderType, AttributeObject
from .helpers.time import get_api_timestring
from .helpers.topoplot import mod_tree, collect_info


def _camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


# This check can be used to stops infinite recursion in some debuggers when stepping into __init__. Debuggers can call
# __dir__ before/during the initialization, and if any class attributes are referred to in both __dir__ and __getattr__
# the call to dir will invoke __getattr__, which in turn will call itself indefinitely
def is_private_attr(attr):
    return attr[0] == '_'


class ProdriskSession(object):

    # Class for handling a Prodrisk session through the python API.

    def __init__(self, license_path='', silent=True, log_file='', solver_path='', suppress_log=False, log_gets=True, sim_id=''):

        # default settings for self
#        if platform.system() == 'Windows':
#            if not license_path:
#                license_path = "C:/prodrisk/lib"
#        else: # covers Linux and Darwin 
#            if not license_path:
#                license_path = "/prodrisk/lib"
        self._n_scenarios = 1
        self._license_path = license_path
        self._silent_console = silent
        self._silent_log = suppress_log
        self._keep_working_directory = False

        os.environ['LTM_CALENDAR'] = 'TRUE'

        if license_path:
            os.environ['LTM_LICENSE_CONTROL_SYSTEM'] = 'TRUE'
            os.environ['LTM_LICENSE_FILE'] = 'LTM_License.dat'  # TODO: cleverly search for LTM_Lice*.dat
            os.environ['LTM_LICENSE_PATH'] = license_path

        # Insert either the solver_path or the LTM_LICENSE_PATH to sys.path to find prodrisk_pybind.pyd

        if solver_path:
            solver_path = os.path.abspath(solver_path)
            sys.path.insert(1, solver_path)
        else:
            sys.path.insert(1, os.environ['LTM_LICENSE_PATH'])

        import prodrisk_pybind as pb

        if sim_id:
            forbidden = ['/', '\\', '*', '"', '<', '>', ':', '|', '?']  # these cannot be used in directory names
            if any([symbol in sim_id for symbol in forbidden]):
                self._session_id = "session_" + pd.Timestamp("now").strftime("%Y-%m-%d-%H-%M-%S")
                print("ProdriskSession: Ignoring argument 'sim_id' because of illegal character.")
                print(f'The session ID is: {self._session_id}')
            else:
                self._session_id = sim_id
        else:
            self._session_id = "session_" + pd.Timestamp("now").strftime("%Y-%m-%d-%H-%M-%S")

        # ProdriskSess(<session_id>, <silentConsoleOutput>, <filePath>)
        if len(log_file) != 0:
            self._pb_api = pb.ProdriskCore(self.session_id, self._silent_console, log_file)
        else:
            self._pb_api = pb.ProdriskCore(self.session_id, self._silent_console)

        # The Prodrisk directory for the current session will be kept. The folder is found under prodrisk.prodrisk_path
        self._pb_api.KeepWorkingDirectory(self._keep_working_directory)

        self.model = ModelBuilderType(self._pb_api, ignores=['setting'])
        self._model = ModelBuilderType(self._pb_api)
        self._setting = self._model.setting.add_object('setting')

        # default settings
        self._settings = {_camel_to_snake(atr): atr for atr in dir(self._setting) if atr[0] != '_'}

        if platform.system() == 'Windows':
            self.prodrisk_path = "C:/prodrisk/bin/"
            self.mpi_path = "C:/Program Files/Microsoft MPI/Bin"
        else: # covers Linux and Darwin 
            self.prodrisk_path = "/prodrisk/bin/"
            self.mpi_path = "/opt/intel/oneapi/mpi/latest/bin"
        self.use_coin_osi = True

    def __dir__(self):
        return [atr for atr in super().__dir__() if atr[0] != '_'] + list(self._settings.keys())

    def __getattr__(self, atr_name):
        # Recursion guard
        if is_private_attr(atr_name):
            return
        if atr_name in self._settings.keys():
            return getattr(self._setting, self._settings[atr_name])
        raise AttributeError(f"{type(self)} has no attribute named '{atr_name}'")

    def __setattr__(self, atr_name, value):
        if self._settings and atr_name in self._settings.keys():
            getattr(self, atr_name).set(value)
            return
        super().__setattr__(atr_name, value)

    @property
    def session_id(self):
        return self._session_id
    
    @property
    def _time_zone(self):
        return self._start_time.tz
    
    @property
    def has_time_zone(self):
        return not (self._time_zone is None)

    @property
    def keep_working_directory(self):
        return self._keep_working_directory

    @keep_working_directory.setter
    def keep_working_directory(self, keep):
        self._pb_api.KeepWorkingDirectory(keep)
        self._keep_working_directory = keep

    @property
    def license_path(self):
        return self._license_path

    # n_scenarios --------

    @property
    def n_scenarios(self):
        return self._n_scenarios

    @n_scenarios.setter
    def n_scenarios(self, n: int):
        assert n > 0, "n_scenarios must be positive"
        self._n_scenarios = n

    # optimization period --------

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def n_weeks(self):
        return self._n_weeks

    def set_optimization_period(self, start_time: pd.Timestamp, n_weeks: int = 52):
        """
            Parameters
            ----------
            start_time: [pandas.Timestamp] start of optimization period
            n_weeks: [integer] number of weeks in optimization period
        """
        self._start_time = pd.Timestamp(start_time)
        self._n_weeks = n_weeks
        self._end_time = start_time + pd.Timedelta(f"{n_weeks}W")
        self._fmt_start_time = get_api_timestring(self._start_time)
        self._fmt_end_time = get_api_timestring(self._end_time)
        self._pb_api.SetOptimizationPeriod(
            self._fmt_start_time,
            self._fmt_end_time,
        )
        if self.has_time_zone:
            self.model.add_time_zone(self._time_zone)
            self._model.add_time_zone(self._time_zone)
            self._setting._timezone = self._time_zone

    def run(self):

        # OPTIMIZE #
        # prodr.optimize()
        status = self._pb_api.GenerateProdriskFiles()
        if status is True:
            status = self._pb_api.RunProdrisk()
            if status is False:
                print("An error occured during the Prodrisk optimization/simulation. Please check the log for details.")
        else:
            print("An error occured, and the Prodrisk optimization/simulation was not run. Please check the log for details.")

        return status

    cut_attributes = {
        'area': ['cutFrequency', 'cutRHS'],
        'module': ['cutCoeffs'],
        'inflowSeries': ['cutCoeffs']
    }

    # Function for dumping the static data in a prodrisk model to yaml
    def dump_model_yaml(self, file_path: str = '.', file_name: str = 'model', direction: str = 'both'):
        import yaml

        #Optimization horizon
        time = {}
        if isinstance(self._start_time, pd.Timestamp):
            time['start_time'] = self._start_time.to_pydatetime()
        else:
            time['start_time'] = self._start_time
        time['n_weeks'] = self._n_weeks
        if self.has_time_zone:
            time['timezone'] = str(self._time_zone)

        #Settings are done separately from other object types since it is special
        setting = {}
        for attr_name in self._settings.keys():
            attr = self.__getattr__(attr_name)
            if not isinstance(attr, AttributeObject):
                continue

            info = attr.info()
            if (direction == 'both' or
                (direction == 'input' and info['isInput'] == 'True') or
                (direction == 'output' and info['isOutput'] == 'True')):
                value = attr.get()
                if value is None or info['datatype'] in ['txy_step', 'txy_stochastic', 'txy', 'xy_array']:
                    continue

                if info['datatype'] in ['xy']:
                    setting[attr_name] = {
                        'name': value.name,
                        'x': value.index.tolist(),
                        'y': value.values.tolist()
                    }
                else:
                    setting[attr_name] = value

        #Loop over all other object types
        model = {}
        for ot in self._pb_api.GetObjectTypeNames():
            if ot == 'setting':
                continue
            
            model[ot] = {}
            for on in self.model[ot].get_object_names():
                model[ot][on] = {}
                for at in self._pb_api.GetObjectTypeAttributeNames(ot):
                    info = self.model[ot][on][at].info()
                    if (direction == 'both' or
                        (direction == 'input' and info['isInput'] == 'True') or
                        (direction == 'output' and info['isOutput'] == 'True')):
                        value = self.model[ot][on][at].get()
                        if value is None or info['datatype'] in ['txy_step', 'txy_stochastic', 'txy', 'xy_array']:
                            continue
                        if ot in self.cut_attributes.keys() and at in self.cut_attributes[ot]:
                            continue  # Cuts should be treated separately

                        if info['datatype'] in ['xy']:
                            model[ot][on][at] = {
                                'name': value.name,
                                'x': value.index.tolist(),
                                'y': value.values.tolist()
                            }
                        else:
                            model[ot][on][at] = value

        if ".yaml" not in file_name:
            file_name += ".yaml"

        yaml_file = os.path.join(file_path, file_name)
        with open(yaml_file, 'w') as outfile:
            yaml.dump({'time': time, 'model': model, 'setting': setting}, outfile, default_flow_style=False)

    # Function for dumping prodrisk timeseries and xy_arrays to h5. Other static data can be dumped to yaml format with dump_model_yaml
    def dump_data_h5(self, file_path: str = '.', file_name: str = 'model', direction: str = 'both'):
            
        if ".h5" not in file_name:
            file_name += ".h5"

        h5_file = os.path.join(file_path, file_name)
        with pd.HDFStore(h5_file, 'w') as store:

            #Do settings first since it is special
            for attr_name in self._settings.keys():
                attr = self.__getattr__(attr_name)
                if not isinstance(attr, AttributeObject):
                    continue

                info = attr.info()
                if (direction == 'both' or
                    (direction == 'input' and info['isInput'] == 'True') or
                    (direction == 'output' and info['isOutput'] == 'True')):
                    value = attr.get()
                    if value is None:
                        continue

                    if info['datatype'] in ['txy_step', 'txy_stochastic', 'txy']:
                        store[f'setting/{attr_name}'] = value
                    elif info['datatype'] in ['xy_array']:
                        for i, v in enumerate(value):
                            store[f'setting/{attr_name}/{i}'] = v

            #Loop over other object types and dump data
            for ot in self._pb_api.GetObjectTypeNames():
                if ot == 'setting':
                    continue
                
                for on in self.model[ot].get_object_names():
                    for at in self._pb_api.GetObjectTypeAttributeNames(ot):
                        info = self.model[ot][on][at].info()
                        if (direction == 'both' or
                            (direction == 'input' and info['isInput'] == 'True') or
                            (direction == 'output' and info['isOutput'] == 'True')):
                            value = self.model[ot][on][at].get()
                            if value is None:
                                continue
                            if ot in self.cut_attributes.keys() and at in self.cut_attributes[ot]:
                                continue  # Cuts should be treated separately
                            
                            if info['datatype'] in ['txy_step', 'txy_stochastic', 'txy']:
                                store[f'{ot}/{on}/{at}'] = value
                            elif info['datatype'] in ['xy_array']:
                                for i, v in enumerate(value):
                                    store[f'{ot}/{on}/{at}/{i}'] = v

    #Dump all cuts to a h5 file
    def dump_cuts_h5(self, file_path: str = '.', file_name: str = 'cuts'):

        if ".h5" not in file_name:
            file_name += ".h5"

        h5_file = os.path.join(file_path, file_name)
        with pd.HDFStore(h5_file, 'w') as store:
            for week in range(self.n_weeks):
                cut_time = self.start_time + pd.Timedelta(weeks=week)
                cut_time_str = dt.datetime.strftime(cut_time, "%Y%m%d%H%M")
                self._pb_api.SetCutTime(cut_time_str)
                self._pb_api.ReadCutResults()
                for ot, attrs in self.cut_attributes.items():
                    for on in self.model[ot].get_object_names():
                        for at in attrs:
                            value = self.model[ot][on][at].get()
                            info = self.model[ot][on][at].info()
                            if value is None:
                                pass
                            else:
                                if info['datatype'] in ['xy_array']:
                                    for i, v in enumerate(value):
                                        store[f'{ot}/{on}/{at}/{week}/{i}'] = v
                                else:
                                    store[f'{ot}/{on}/{at}/{week}'] = value
            # Save attributes required for simulation with given cuts
            for on in self.model.module.get_object_names():
                for at in ['MeanReservoirTrajectories', 'HeadCoefficient']:
                    store[f'module/{on}/{at}'] = self.model.module[on][at].get()

    # Function loading a static yaml model into ProdriskSession
    def load_model_yaml(self, file_path: str = '.', file_name: str = 'model'):
        import yaml

        if ".yaml" not in file_name:
            file_name += ".yaml"

        yaml_file = os.path.join(file_path, file_name)
        with open(yaml_file, 'r') as file:
            full_model = yaml.safe_load(file)

        #Set optimization horizon if data is present in the file
        try:
            time = full_model['time']
            if 'timezone' in time.keys():
                t1 = pd.Timestamp(time['start_time']).tz_convert(time['timezone'])
            else:
                t1 = pd.Timestamp(time['start_time'])
            self.set_optimization_period(t1, time['n_weeks'])
        except KeyError:
            pass

        try:
            model = full_model['model']
        except KeyError:
            model = {}      

        #Set static model data if present in the file
        for ot, objs in model.items():
            for obj_name, attrs in objs.items():
                if not obj_name in self.model[ot].get_object_names():
                    self.model[ot].add_object(obj_name)
                for attr_name, value in attrs.items():
                    info = self.model[ot][obj_name][attr_name].info()
                    if info['datatype'] == 'xy':
                        self.model[ot][obj_name][attr_name].set(pd.Series(
                            name=value['name'],
                            index=value['x'],
                            data=value['y']
                        ))
                    else:
                        self.model[ot][obj_name][attr_name].set(value)

        #Set prodrisk settings if present in the file
        try:
            setting = full_model['setting']
        except KeyError:
            setting = {}      

        for attr_name, value in setting.items():
            info = self.__getattr__(attr_name).info()
            if info['datatype'] == 'xy':
                self.__getattr__(attr_name).set(pd.Series(
                    name=value['name'],
                    index=value['x'],
                    data=value['y']
                ))
            else:
                self.__getattr__(attr_name).set(value)
    
    #Function for loading in timeseries and xy_array data on h5 files previously dumped from ProdriskSession
    def load_data_h5(self, file_path: str = '.', file_name: str = 'model'):

        if ".h5" not in file_name:
            file_name += ".h5"

        h5_file = os.path.join(file_path, file_name)
        with pd.HDFStore(h5_file, 'r') as store:
            store_keys = np.array(store.keys())
            for k in store_keys:
                k_split = k.split('/')
                ot = k_split[1]
                if ot == 'setting':
                    at = k_split[2]
                    attr = self.__getattr__(at)
                else:
                    on = k_split[2]
                    at = k_split[3]
                    attr = self.model[ot][on][at]

                info = attr.info()

                if info['datatype'] == 'xy_array':
                    if ot in self.cut_attributes.keys() and at in self.cut_attributes[ot]:
                        continue  # Cuts are loaded separately

                    id = int(k_split[4])
                    if id == 0:
                        res_arr = []
                        while (f'/{ot}/{on}/{at}/{id}' in store_keys):
                            res_arr.append(store[f'{ot}/{on}/{at}/{id}'])
                            id += 1
                        attr.set(res_arr)
                else:
                    attr.set(store[k])

    #Load in cuts that were previously dumped by the dump_cuts_h5 function
    def load_cuts_h5(self, file_path: str = '.', file_name: str = 'cuts'):

        if ".h5" not in file_name:
            file_name += ".h5"

        h5_file = os.path.join(file_path, file_name)
        with pd.HDFStore(h5_file, 'r') as store:
            store_keys = store.keys()
            for week in range(self._n_weeks):
                cut_time = self.start_time + pd.Timedelta(weeks=week)
                cut_time_str = dt.datetime.strftime(cut_time, "%Y%m%d%H%M")
                self._pb_api.SetCutTime(cut_time_str)
                for ot, _ in self.cut_attributes.items():
                    for on in self.model[ot].get_object_names():
                        for at in self.cut_attributes[ot]:
                            res_arr = []
                            for id in range(self.n_price_levels.get()):
                                if f'/{ot}/{on}/{at}/{week}/{id}' in store_keys:
                                    res_arr.append(store[f'{ot}/{on}/{at}/{week}/{id}'])
                            self.model[ot][on][at].set(res_arr)
                self._pb_api.WriteCutResults()

                # Load attributes required for simulation with given cuts
                for on in self.model.module.get_object_names():
                    for at in ['MeanReservoirTrajectories', 'HeadCoefficient']:
                        self.model.module[on][at].set(store[f'module/{on}/{at}'])

    def plot_topology(self, to_file=""):
        module_tree = mod_tree(collect_info(self))
        module_tree.plot_topology(axtitle=self._session_id ,to_file=to_file)
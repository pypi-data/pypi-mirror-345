from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType,\
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand # object used to send info back to the main thread
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_bnc.hardware.bnc_commands import BNC575
from qtpy import QtCore
from typing import Union, List, Dict, Tuple


class DAQ_Move_bnc(DAQ_Move_base):
    """ Instrument plugin class for an actuator.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

        * This is compatible with the BNC 575 Delay/Pulse Generator
        * Tested on PyMoDAQ 4.1.1
        * Tested on Python 3.8.18
        * No additional drivers necessary

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    is_multiaxes = False
    _axis_names: Union[List[str], Dict[str, int]] = ['Delay']
    _controller_units: Union[str, List[str]] = 'ns'
    _epsilon = 0.25
    data_actuator_type = DataActuatorType.DataActuator

    params = comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: BNC575 = None
        self.attributes = None

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The delay obtained after scaling conversion.
        """
        delay = DataActuator(data=self.controller.get_delay()*1e9)
        delay = self.get_position_with_scaling(delay)

        return delay
    
    def user_condition_to_reach_target(self) -> bool:
        """ Implement a condition for exiting the polling mechanism and specifying that the
        target value has been reached

       Returns
        -------
        bool: if True, PyMoDAQ considers the target value has been reached
        """
        if self.controller.get_delay() == self.settings.child('output', 'delay'):
            return True
        else:
            return False 

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close()

    def get_config(self):
        """Get current parameters and update their values in the UI"""
        self.attributes = self.controller.output()
        self.update_params_ui()


    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "ip":
            port = self.controller.port
            self.close()
            self.controller = self.ini_stage_init(old_controller=None,
                                              new_controller=BNC575(param.value(), port))
        if param.name() == "port":
            ip = self.controller.ip
            self.close()
            self.controller = self.ini_stage_init(old_controller=None,
                                              new_controller=BNC575(ip, param.value()))
        elif param.name() == "label":
            self.controller.set_label(param.value())
        elif param.name() == "slot":
           self.controller.slot = param.value()
        elif param.name() == "save":
            if param.value:
                self.controller.save_state()
        elif param.name() == "restore":
            if param.value:
                self.controller.restore_state()
                self.get_config()
        elif param.name() == "reset":
            if param.value:
                self.controller.reset()
                self.get_config()
        elif param.name() == "global_state":
            if param.value():
                self.controller.set_global_state('ON')
            else param.value():
                self.controller.set_global_state('OFF')    
        elif param.name() == "global_mode":
            self.controller.set_global_mode(param.value())
        elif param.name() == "channel_state":
            if param.value():
                self.controller.set_global_state('ON')
            else param.value():
                self.controller.set_global_state('OFF')
        elif param.name() == "channel_mode":
            self.controller.set_channel_mode(param.value())
        elif param.name() == "channel_label":
           self.controller.channel_label = param.value()
           self.get_config()
        elif param.name() == "delay":
            self.controller.set_delay(param.value()) * 1e-9
            self.get_actuator_value()
        elif param.name() == "width":
            self.controller.set_width(param.value()) * 1e-9
        elif param.name() == "amplitude_mode":
            self.controller.set_amplitude_mode(param.value())
        elif param.name() == "amplitude":
            self.controller.set_amplitude(param.value())
        elif param.name() == "polarity":
            self.controller.set_polarity(param.value())
        elif param.name() == "period":
            self.controller.set_period(param.value())
            self.settings.child('continuous_mode',  'rep_rate').setValue(1 / self.controller.get_period())
        elif param.name() == "rep_rate":
            self.controller.set_period(1 / param.value())
            self.settings.child('continuous_mode',  'period').setValue(self.controller.get_period())
        elif param.name() == "trig_mode":
            self.controller.set_trig_mode(param.value())
        elif param.name() == "trig_thresh":
            self.controller.set_trig_thresh(param.value())
        elif param.name() == "trig_edge":
            self.controller.set_trig_edge(param.value())
        elif param.name() == "gate_mode":
            self.controller.set_gate_mode(param.value())
        elif param.name() == "channel_gate_mode":
            self.controller.set_channel_gate_mode(param.value())
            self.settings.child('gating',  'gate_mode').setValue(self.controller.get_gate_mode())
        elif param.name() == "gate_thresh":
            self.controller.set_gate_thresh(param.value())
        elif param.name() == "gate_logic":            
            self.controller.set_gate_logic(param.value())

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.ini_stage_init(slave_controller=controller)  # will be useful when controller is slave

        if self.is_master:  # is needed when controller is master
            self.controller = BNC575("192.168.178.146", 2001)
        
        # Initialize device state
        self.settings.child('connection',  'ip').setValue(self.controller.ip)
        self.settings.child('connection',  'port').setValue(self.controller.port)
        self.controller.restore_state()

        # Update UI with relevant parameters & their current values
        self.attributes = self.controller.output()
        self.settings.addChildren(self.attributes)
        self.update_params_ui()
        self.settings.child('bounds').hide()
        self.settings.child('scaling').hide()
        self.settings.child('units').hide()
        self.settings.child('epsilon').hide()
        

        info = "Device initialized successfully"
        initialized = True
        return info, initialized


    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value
        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """
        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        self.controller.set_delay(self.target_value * 1e-9)

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value
        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)
        self.controller.set_delay(self.target_value * 1e-9)
        self.emit_status(ThreadCommand('Update_Status', ['Moving delay by: {}'.format(value.value())]))

    def move_home(self):
        """Call the reference method of the controller"""
        self.controller.set_delay(0)
        self.emit_status(ThreadCommand('Update_Status', ['Moving to zero position']))
        self.poll_moving()

    def stop_motion(self):
      """Stop the actuator and emits move_done signal"""
      self.move_done()
      self.poll_moving()

    def update_params_ui(self):
        # Update UI with current parameter values
        for param in self.attributes:
            param_type = param['type']
            param_name = param['name']
            
            if param_type == 'group':
                # Recurse over children in groups
                for child in param['children']:
                    child_name = child['name']
                    try:
                        value = child['value']
                    except Exception as e:
                        continue

                    try:
                        # Set the value
                        self.settings.child(param_name, child_name).setValue(value)

                        # Set limits if defined
                        if 'limits' in child and not child.get('readonly', False):
                            try:
                                limits = child['limits']
                                self.settings.child(param_name, child_name).setLimits(limits)
                            except Exception:
                                pass

                    except Exception:
                        pass
            else:
                try:
                    value = param['value']
                except Exception as e:
                    continue

                try:
                    # Set the value
                    self.settings.param(param_name).setValue(value)

                    if 'limits' in param and not param.get('readonly', False):
                        try:
                            limits = param['limits']
                            self.settings.param(param_name).setLimits(limits)
                        except Exception:
                            pass
                except Exception:
                    pass


if __name__ == '__main__':
    main(__file__)

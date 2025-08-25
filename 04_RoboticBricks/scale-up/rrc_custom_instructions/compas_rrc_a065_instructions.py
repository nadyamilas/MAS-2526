from compas_fab.backends.ros.messages import ROSmsg
from compas_robots import Configuration
from compas_rrc.common import ExecutionLevel, FeedbackLevel
from compas_rrc.motion import Motion
from compas_rrc.motion import MoveGeneric

INSTRUCTION_PREFIX = 'r_A065_'

__all__ = [
    'MoveToPrintStart',
    'MoveToPrint',
    'MoveToPrintEnd',
    'MoveToHcPrintStart',
    'MoveToHcPrint',
    'MoveToHcPrintEnd',
]


class MoveToPrintStart(MoveGeneric):
    """Move to arc start is a call that moves the robot in the cartisian space to the arc start position and will start the weld. 

    RAPID Instruction: ``r_A065_MoveToPrintStart`` 

    Attributes:

        frame (:class:`compas.geometry.Frame`):
            Target frame.

        ext_axes (:class:`compas_rrc.common.ExternalAxes` or :obj:`list` of :obj:`float`):
            External axes positions.

        speed (:obj:`int`):
            Integer specifying TCP translational speed in mm/s. Min=``0.01``.

        zone (:class:`Zone`):
            Zone data. Predefined in the robot controller,
            only Zone ``fine`` will do a stop point all others are fly by points

        layer_height (:obj: `int`):
            Height of the layer [mm]

        layer_width (:obj: `int`):
            Width of the layer [mm]

        material_constant (:obj: `int`):
            Material constant usually between 1000 - 2000 [none]

        start_setpoint (:obj: `int`):
            Extrusion speed before motion start [rpm]

        start_time (:obj: `int`):
            Time to extrude before motion start [s]

        follow_speed (:obj:`int`):
            Integer specifying TCP translational speed from following move instruction in mm/s. Min=``0.01``.

        motion_type (:class:`Motion`):
            Motion type. Defaults to Linear.

        feedback_level (:obj:`int`):
            Integer specifying requested feedback level. Default=``0`` (i.e. ``NONE``).
            Feedback level is instruction-specific but the value ``1`` always represents
            completion of the instruction.

    """

    def __init__(self, frame, ext_axes, speed, zone, layer_height, layer_width, material_constant, start_setpoint, start_time, follow_speed, motion_type=Motion.LINEAR, feedback_level=FeedbackLevel.NONE):
        super(MoveToPrintStart, self).__init__(
            frame, ext_axes, speed, zone, feedback_level)
        self.instruction = INSTRUCTION_PREFIX + 'MoveToPrintStart'
        self.exec_level = ExecutionLevel.ROBOT

        move_type = 'J' if motion_type == Motion.JOINT else 'L'
        self.string_values = [move_type]
        self.float_values.extend([layer_height, layer_width, material_constant, start_setpoint, start_time, follow_speed])


class MoveToPrint(MoveGeneric):
    """Move to arc start is a call that moves the robot in the cartisian space to the arc start position and will start the weld. 

    RAPID Instruction: ``r_A065_MoveToPrint`` 

    Attributes:

        frame (:class:`compas.geometry.Frame`):
            Target frame.

        ext_axes (:class:`compas_rrc.common.ExternalAxes` or :obj:`list` of :obj:`float`):
            External axes positions.

        speed (:obj:`int`):
            Integer specifying TCP translational speed in mm/s. Min=``0.01``.

        zone (:class:`Zone`):
            Zone data. Predefined in the robot controller,
            only Zone ``fine`` will do a stop point all others are fly by points

        layer_height (:obj: `int`):
            Height of the layer [mm]

        layer_width (:obj: `int`):
            Width of the layer [mm]

        material_constant (:obj: `int`):
            Material constant usually between 1000 - 2000 [none]

        motion_type (:class:`Motion`):
            Motion type. Defaults to Linear.

        feedback_level (:obj:`int`):
            Integer specifying requested feedback level. Default=``0`` (i.e. ``NONE``).
            Feedback level is instruction-specific but the value ``1`` always represents
            completion of the instruction.

    """

    def __init__(self, frame, ext_axes, speed, zone, layer_height, layer_width, material_constant, motion_type=Motion.LINEAR, feedback_level=FeedbackLevel.NONE):
        super(MoveToPrint, self).__init__(
            frame, ext_axes, speed, zone, feedback_level)
        self.instruction = INSTRUCTION_PREFIX + 'MoveToPrint'
        self.exec_level = ExecutionLevel.ROBOT

        move_type = 'J' if motion_type == Motion.JOINT else 'L'
        self.string_values = [move_type]
        self.float_values.extend([layer_height, layer_width, material_constant])


class MoveToPrintEnd(MoveGeneric):
    """Move to arc start is a call that moves the robot in the cartisian space to the arc start position and will start the weld. 

    RAPID Instruction: ``r_A065_MoveToPrintEnd`` 

    Attributes:

        frame (:class:`compas.geometry.Frame`):
            Target frame.

        ext_axes (:class:`compas_rrc.common.ExternalAxes` or :obj:`list` of :obj:`float`):
            External axes positions.

        speed (:obj:`int`):
            Integer specifying TCP translational speed in mm/s. Min=``0.01``.

        zone (:class:`Zone`):
            Zone data. Predefined in the robot controller,
            only Zone ``fine`` will do a stop point all others are fly by points

        layer_height (:obj: `int`):
            Height of the layer [mm]

        layer_width (:obj: `int`):
            Width of the layer [mm]

        material_constant (:obj: `int`):
            Material constant usually between 1000 - 2000 [none]

        end_time (:obj: `int`):
            Time to stop extrusion before coninuing [s]

        motion_type (:class:`Motion`):
            Motion type. Defaults to Linear.

        feedback_level (:obj:`int`):
            Integer specifying requested feedback level. Default=``0`` (i.e. ``NONE``).
            Feedback level is instruction-specific but the value ``1`` always represents
            completion of the instruction.

    """

    def __init__(self, frame, ext_axes, speed, zone, layer_height, layer_width, material_constant, end_time, motion_type=Motion.LINEAR, feedback_level=FeedbackLevel.NONE):
        super(MoveToPrintEnd, self).__init__(
            frame, ext_axes, speed, zone, feedback_level)
        self.instruction = INSTRUCTION_PREFIX + 'MoveToPrintEnd'
        self.exec_level = ExecutionLevel.ROBOT

        move_type = 'J' if motion_type == Motion.JOINT else 'L'
        self.string_values = [move_type]
        self.float_values.extend([layer_height, layer_width, material_constant, end_time])


######## HC related instructions ##########
        
class MoveToHcPrintStart(MoveGeneric):
    """Move to arc start is a call that moves the robot in the cartisian space to the arc start position and will start the weld. 

    RAPID Instruction: ``r_A065_MoveToPrintStart`` 

    Attributes:

        frame (:class:`compas.geometry.Frame`):
            Target frame.

        ext_axes (:class:`compas_rrc.common.ExternalAxes` or :obj:`list` of :obj:`float`):
            External axes positions.

        speed (:obj:`int`):
            Integer specifying TCP translational speed in mm/s. Min=``0.01``.

        zone (:class:`Zone`):
            Zone data. Predefined in the robot controller,
            only Zone ``fine`` will do a stop point all others are fly by points
        
        hollowcore_setpoint (:obj: 'float'):
            this value serves to calculate the RPM of the extruder, which follows the following formula:

            RPM setpoint = current_speed * hollow_core_setpoint
            Hollow_core_setpoint = ((HCnozzleOuterRad^2 - HCnozzleinnerRad^2) / AdmissionRad^2) * HCconstant
            Hollow_core_setpoint = ((12*12 - 11.5*11.5)/10*10) * 0.2 = 0.0235

            RPM = current_speed * 0.0235 [rpm]

            RPM should not exceed 20 RPM in the screen of the CEAD extruder
            torque should not exceed 70%
            utilization should not exceed 90%

        hollow_core_air_pressure (:obj: `float`):
            values between 4 mba and 20 mba

            min val for actual min air pressure 4.09
            max val for actual max air pressure 16

        start_setpoint (:obj: `int`):
            Extrusion speed before motion start [rpm]

        start_time (:obj: `int`):
            Time to extrude before motion start [s]

        follow_speed (:obj:`int`):
            Integer specifying TCP translational speed from following move instruction in mm/s. Min=``0.01``.

        motion_type (:class:`Motion`):
            Motion type. Defaults to Linear.

        feedback_level (:obj:`int`):
            Integer specifying requested feedback level. Default=``0`` (i.e. ``NONE``).
            Feedback level is instruction-specific but the value ``1`` always represents
            completion of the instruction.

    """

    def __init__(self, frame, ext_axes, speed, zone, hollowcore_setpoint, hollow_core_air_pressure, start_setpoint, start_time, follow_speed, motion_type=Motion.LINEAR, feedback_level=FeedbackLevel.NONE):
        super(MoveToHcPrintStart, self).__init__(
            frame, ext_axes, speed, zone, feedback_level)
        self.instruction = INSTRUCTION_PREFIX + 'MoveToHcPrintStart'
        self.exec_level = ExecutionLevel.ROBOT

        move_type = 'J' if motion_type == Motion.JOINT else 'L'
        self.string_values = [move_type]
        self.float_values.extend([hollowcore_setpoint, hollow_core_air_pressure, start_setpoint, start_time, follow_speed])


class MoveToHcPrint(MoveGeneric):
    """Move to arc start is a call that moves the robot in the cartisian space to the arc start position and will start the weld. 

    RAPID Instruction: ``r_A065_MoveToPrint`` 

    Attributes:

        frame (:class:`compas.geometry.Frame`):
            Target frame.

        ext_axes (:class:`compas_rrc.common.ExternalAxes` or :obj:`list` of :obj:`float`):
            External axes positions.

        speed (:obj:`int`):
            Integer specifying TCP translational speed in mm/s. Min=``0.01``.

        zone (:class:`Zone`):
            Zone data. Predefined in the robot controller,
            only Zone ``fine`` will do a stop point all others are fly by points

        hollowcore_setpoint (:obj: 'float'):
            this value serves to calculate the RPM of the extruder, which follows the following formula:

            RPM setpoint = current_speed * hollow_core_setpoint
            Hollow_core_setpoint = ((HCnozzleOuterRad^2 - HCnozzleinnerRad^2) / AdmissionRad^2) * HCconstant
            Hollow_core_setpoint = ((12*12 - 11.5*11.5)/10*10) * 0.2 = 0.0235

            RPM = current_speed * 0.0235 [rpm]

            RPM should not exceed 20 RPM in the screen of the CEAD extruder
            torque should not exceed 70%
            utilization should not exceed 90%

        hollow_core_air_pressure (:obj: `float`):
            values between 4 mba and 20 mba

            min val for actual min air pressure 4.09
            max val for actual max air pressure 16

        motion_type (:class:`Motion`):
            Motion type. Defaults to Linear.

        feedback_level (:obj:`int`):
            Integer specifying requested feedback level. Default=``0`` (i.e. ``NONE``).
            Feedback level is instruction-specific but the value ``1`` always represents
            completion of the instruction.

    """

    def __init__(self, frame, ext_axes, speed, zone, hollowcore_setpoint, hollow_core_air_pressure, motion_type=Motion.LINEAR, feedback_level=FeedbackLevel.NONE):
        super(MoveToHcPrint, self).__init__(
            frame, ext_axes, speed, zone, feedback_level)
        self.instruction = INSTRUCTION_PREFIX + 'MoveToHcPrint'
        self.exec_level = ExecutionLevel.ROBOT

        move_type = 'J' if motion_type == Motion.JOINT else 'L'
        self.string_values = [move_type]
        self.float_values.extend([hollowcore_setpoint, hollow_core_air_pressure])


class MoveToHcPrintEnd(MoveGeneric):
    """Move to arc start is a call that moves the robot in the cartisian space to the arc start position and will start the weld. 

    RAPID Instruction: ``r_A065_MoveToPrintEnd`` 

    Attributes:

        frame (:class:`compas.geometry.Frame`):
            Target frame.

        ext_axes (:class:`compas_rrc.common.ExternalAxes` or :obj:`list` of :obj:`float`):
            External axes positions.

        speed (:obj:`int`):
            Integer specifying TCP translational speed in mm/s. Min=``0.01``.

        zone (:class:`Zone`):
            Zone data. Predefined in the robot controller,
            only Zone ``fine`` will do a stop point all others are fly by points
        
        hollowcore_setpoint (:obj: 'float'):
            this value serves to calculate the RPM of the extruder, which follows the following formula:

            RPM setpoint = current_speed * hollow_core_setpoint
            Hollow_core_setpoint = ((HCnozzleOuterRad^2 - HCnozzleinnerRad^2) / AdmissionRad^2) * HCconstant
            Hollow_core_setpoint = ((12*12 - 11.5*11.5)/10*10) * 0.2 = 0.0235

            RPM = current_speed * 0.0235 [rpm]

            RPM should not exceed 20 RPM in the screen of the CEAD extruder
            torque should not exceed 70%
            utilization should not exceed 90%

        hollow_core_air_pressure (:obj: `float`):
            values between 4 mba and 20 mba

            min val for actual min air pressure 4.09
            max val for actual max air pressure 16

        end_time (:obj: `int`):
            Time to stop between extrusion has finished and hollowcore air turns off [s]

        motion_type (:class:`Motion`):
            Motion type. Defaults to Linear.

        feedback_level (:obj:`int`):
            Integer specifying requested feedback level. Default=``0`` (i.e. ``NONE``).
            Feedback level is instruction-specific but the value ``1`` always represents
            completion of the instruction.

    """

    def __init__(self, frame, ext_axes, speed, zone, hollowcore_setpoint, hollow_core_air_pressure, end_time, motion_type=Motion.LINEAR, feedback_level=FeedbackLevel.NONE):
        super(MoveToHcPrintEnd, self).__init__(
            frame, ext_axes, speed, zone, feedback_level)
        self.instruction = INSTRUCTION_PREFIX + 'MoveToHcPrintEnd'
        self.exec_level = ExecutionLevel.ROBOT

        move_type = 'J' if motion_type == Motion.JOINT else 'L'
        self.string_values = [move_type]
        self.float_values.extend([hollowcore_setpoint, hollow_core_air_pressure, end_time])


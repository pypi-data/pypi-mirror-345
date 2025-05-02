from enum import Enum
from typing import Union, Tuple
from ...core.instrument import Instrument, mark_query, mark_command


class SystemStatusM(Enum):
	NORMAL = 0
	QUENCHED = 1
	OVERHEATED = 2
	WARMING_UP = 4
	FAULT = 8


class SystemStatusMModel(Enum):
	NORMAL = 'Normal'
	QUENCHED = 'Quenched'
	OVERHEATED = 'Overheaded'
	WARMING_UP = 'Warming up'
	FAULT = 'Fault'


class SystemStatusN(Enum):
	NORMAL = 0
	POSITIVE_VOLTAGE_LIMIT = 1
	NEGATIVE_VOLTAGE_LIMIT = 2
	NEGATIVE_CURRENT_LIMIT = 4
	POSITIVE_CURRENT_LIMIT = 8


class SystemStatusNModel(Enum):
	NORMAL = 'Normal'
	POSITIVE_VOLTAGE_LIMIT = 'On positive voltage limit'
	NEGATIVE_VOLTAGE_LIMIT = 'On negative voltage limit'
	NEGATIVE_CURRENT_LIMIT = 'Outside negative current limit'
	POSITIVE_CURRENT_LIMIT = 'Outside positive current limit'


class ActivityStatus(Enum):
	HOLD = 0
	TO_SETPOINT = 1
	TO_ZERO = 2
	CLAMPED = 4


class ActivityStatusModel(Enum):
	HOLD = 'Hold'
	TO_SETPOINT = 'To setpoint'
	TO_ZERO = 'To zero'
	CLAMPED = 'Clamped'


class RemoteStatus(Enum):
	LOCAL_LOCKED = 0
	REMOTE_LOCKED = 1
	LOCAL_UNLOCKED = 2
	REMOTE_UNLOCKED = 3


class RemoteStatusModel(Enum):
	LOCAL_LOCKED = 'Local and locked'
	REMOTE_LOCKED = 'Remote and locked'
	LOCAL_UNLOCKED = 'Local and unlocked'
	REMOTE_UNLOCKED = 'Remote and unlocked'


class SwitchHeaterStatus(Enum):
	OFF_AT_ZERO = 0
	ON = 1
	OFF_AT_FIELD = 2
	FAULT = 3
	NOT_FITTED = 4


class SwitchHeaterStatusModel(Enum):
	OFF_AT_ZERO = 'Off (closed) at zero field'
	ON = 'On (open)'
	OFF_AT_FIELD = 'Off (closed) at field'
	FAULT = 'Fault'
	NOT_FITTED = 'Not fitted'


class ModeStatusM(Enum):
	FAST_AMPS = 0
	FAST_TESLA = 1
	SLOW_AMPS = 4
	SLOW_TESLA = 5


class ModeStatusMModel(Enum):
	FAST_AMPS = 'Fast sweep (amps)'
	FAST_TESLA = 'Fast sweep (tesla)'
	SLOW_AMPS = 'Slow sweep (amps)'
	SLOW_TESLA = 'Slow sweep (tesla)'


class ModeStatusN(Enum):
	REST = 0
	SWEEPING = 1
	LIMITING = 2
	SWEEPING_LIMITING = 3


class ModeStatusNModel(Enum):
	REST = 'At rest (constant output)'
	SWEEPING = 'Sweeping'
	LIMITING = 'Sweep limiting'
	SWEEPING_LIMITING = 'Sweeping and sweep limiting'







class Mercury_IPS(Instrument):


	name = 'Mercury_IPS'


	@mark_query
	def identify(self) -> str:
		return self.query("*IDN?")


	@mark_query
	def remote_and_locked(self) -> str:
		return self.query('C1')


	@mark_query
	def local_and_unlocked(self) -> str:
		return self.query('C2')


	@mark_query
	def remote_and_unlocked(self) -> str:
		return self.query('C3')


	@mark_query
	def get_output_current(self) -> float:
		return float(self.query("R0")[1:])


	@mark_query
	def get_supply_voltage(self) -> float:
		return float(self.query("R1")[1:])


	@mark_query
	def get_magnet_current(self) -> float:
		return float(self.query("R2")[1:])


	@mark_query
	def get_setpoint_current(self) -> float:
		return float(self.query("R5")[1:])


	@mark_query
	def get_current_sweep_rate(self) -> float:
		return float(self.query("R6")[1:])


	@mark_query
	def get_output_field(self) -> float:
		return float(self.query("R7")[1:])


	@mark_query
	def get_setpoint_field(self) -> float:
		return float(self.query("R8")[1:])


	@mark_query
	def get_field_sweep_rate(self) -> float:
		return float(self.query("R9")[1:])


	@mark_query
	def get_software_voltage_limit(self) -> float:
		return float(self.query("R15")[1:])


	@mark_query
	def get_persistent_current(self) -> float:
		return float(self.query("R16")[1:])


	@mark_query
	def get_trip_current(self) -> float:
		return float(self.query("R17")[1:])


	@mark_query
	def get_persistent_field(self) -> float:
		return float(self.query("R18")[1:])


	@mark_query
	def get_trip_field(self) -> float:
		return float(self.query("R19")[1:])


	@mark_query
	def get_switch_heater_current(self) -> float:
		response = float(self.query("R20")[1:-2])
		return response*1e-3


	@mark_query
	def get_negative_current_limit(self) -> float:
		return float(self.query("R21")[1:])


	@mark_query
	def get_positive_current_limit(self) -> float:
		return float(self.query("R22")[1:])


	@mark_query
	def get_lead_resistance(self) -> float:
		return float(self.query("R23")[1:-1])


	@mark_query
	def get_magnet_inductance(self) -> float:
		return float(self.query("R24")[1:])


	# @mark_query
	# def get_status(self) -> float:
	# 	response = self.query("X")
	# 	Xm = response[1]
	# 	Xn = response[2]
	# 	An = response[4]
	# 	Cn = response[6]
	# 	Hn = response[8]
	# 	Mm = response[10]
	# 	Mn = response[11]
	# 	return {
	# 		'system': [SystemStatusM(Xm)]
	# 	}


	def _parse_status_string(self, string: str, index: int):

		if not isinstance(string, str):
			raise TypeError(f'Expected to receive a string, got {type(string).__name__}')

		elif len(string) not in [12, 15]:
			raise ValueError(f'Expected status string of length 12 or 15, got {string} (len {len(string)})')

		elif string[0] != 'X':
			raise ValueError(f'"X" not found at string[0]. Expected string of form XmnAnCnHnMmnPmn, got {string}')

		elif string[3] != 'A':
			raise ValueError(f'"A" not found at string[3]. Expected string of form XmnAnCnHnMmnPmn, got {string}')

		else:
			return string[index]


	@mark_query 
	def get_system_status(self) -> SystemStatusM:
		response = self.query("X")
		response = self._parse_status_string(response, 1)
		return SystemStatusM(int(response))


	@mark_query
	def get_limit_status(self) -> SystemStatusN:
		response = self.query("X")
		response = self._parse_status_string(response, 2)
		return SystemStatusN(int(response))


	@mark_query
	def get_activity_status(self) -> ActivityStatus:
		response = self.query("X")
		response = self._parse_status_string(response, 4)
		return ActivityStatus(int(response))


	@mark_query
	def get_remote_status(self) -> RemoteStatus:
		response = self.query("X")
		response = self._parse_status_string(response, 6)
		return RemoteStatus(int(response))


	@mark_query
	def get_switch_heater_status(self) -> SwitchHeaterStatus:
		response = self.query("X")
		response = self._parse_status_string(response, 8)
		return SwitchHeaterStatus(int(response))


	@mark_query
	def get_sweep_mode_status(self) -> ModeStatusM:
		response = self.query("X")
		response = self._parse_status_string(response, 10)
		return ModeStatusM(int(response))


	@mark_query
	def get_sweep_status(self) -> ModeStatusN:
		response = self.query("X")
		response = self._parse_status_string(response, 11)
		return ModeStatusN(int(response))


	@mark_query
	def hold(self) -> int:
		return self.query("A0")


	@mark_query
	def to_setpoint(self) -> int:
		return self.query("A1")


	@mark_query
	def to_zero(self) -> int:
		return self.query("A2")


	@mark_query
	def clamp(self) -> int:
		return self.query("A4")


	@mark_query
	def heater_off(self) -> str:
		return self.query("H0")


	@mark_query
	def heater_on(self) -> str:
		return self.query("H1")


	@mark_query
	def force_heater_on(self) -> int:
		return self.query("H2")


	@mark_query
	def set_target_current(self, current: float) -> int:
		return self.query(f"I{current:.3f}")


	@mark_query
	def set_target_field(self, field: float) -> int:
		return self.query(f"J{field:.3f}")


	@mark_query
	def set_current_sweep_rate(self, rate: float) -> int:
		return self.query(f"S{rate:.3f}")


	@mark_query
	def set_field_sweep_rate(self, rate: float) -> int:
		return self.query(f"T{rate:.3f}")





	def register_endpoints(self, api_server) -> None:
		super().register_endpoints(api_server)


		@api_server.app.get(f'/{self._uid}/identify', tags=[self._uid])
		async def identify() -> str:
			return self.identify()


		@api_server.app.get(f'/{self._uid}/set/remote_and_locked', tags=[self._uid])
		async def set_remote_and_locked() -> str:
			return self.remote_and_locked()


		@api_server.app.get(f'/{self._uid}/set/local_and_unlocked', tags=[self._uid])
		async def set_remote_and_locked() -> str:
			return self.local_and_unlocked()


		@api_server.app.get(f'/{self._uid}/set/remote_and_unlocked', tags=[self._uid])
		async def set_remote_and_locked() -> str:
			return self.remote_and_unlocked()


		@api_server.app.get(f'/{self._uid}/get/output_current', tags=[self._uid])
		async def get_output_current() -> float:
			return self.get_output_current()


		@api_server.app.get(f'/{self._uid}/get/supply_voltage', tags=[self._uid])
		async def get_supply_voltage() -> float:
			return self.get_supply_voltage()


		@api_server.app.get(f'/{self._uid}/get/magnet_current', tags=[self._uid])
		async def get_magnet_current() -> float:
			return self.get_magnet_current()


		@api_server.app.get(f'/{self._uid}/get/setpoint_current', tags=[self._uid])
		async def get_setpoint_current() -> float:
			return self.get_setpoint_current()


		@api_server.app.get(f'/{self._uid}/get/current_sweep_rate', tags=[self._uid])
		async def get_current_sweep_rate() -> float:
			return self.get_current_sweep_rate()


		@api_server.app.get(f'/{self._uid}/get/output_field', tags=[self._uid])
		async def get_output_field() -> float:
			return self.get_output_field()


		@api_server.app.get(f'/{self._uid}/get/setpoint_field', tags=[self._uid])
		async def get_setpoint_field() -> float:
			return self.get_setpoint_field()


		@api_server.app.get(f'/{self._uid}/get/field_sweep_rate', tags=[self._uid])
		async def get_field_sweep_rate() -> float:
			return self.get_field_sweep_rate()


		@api_server.app.get(f'/{self._uid}/get/software_voltage_limit', tags=[self._uid])
		async def get_software_voltage_limit() -> float:
			return self.get_software_voltage_limit()


		@api_server.app.get(f'/{self._uid}/get/persistant_current', tags=[self._uid])
		async def get_persistant_current() -> float:
			return self.get_persistant_current()


		@api_server.app.get(f'/{self._uid}/get/trip_current', tags=[self._uid])
		async def get_trip_current() -> float:
			return self.get_trip_current()


		@api_server.app.get(f'/{self._uid}/get/persistant_field', tags=[self._uid])
		async def get_persistant_field() -> float:
			return self.get_persistant_field()


		@api_server.app.get(f'/{self._uid}/get/trip_field', tags=[self._uid])
		async def get_trip_field() -> float:
			return self.get_trip_field()


		@api_server.app.get(f'/{self._uid}/get/switch_heater_current', tags=[self._uid])
		async def get_switch_heater_current() -> float:
			return self.get_switch_heater_current()


		@api_server.app.get(f'/{self._uid}/get/negative_current_limit', tags=[self._uid])
		async def get_negative_current_limit() -> float:
			return self.get_negative_current_limit()


		@api_server.app.get(f'/{self._uid}/get/positive_current_limit', tags=[self._uid])
		async def get_positive_current_limit() -> float:
			return self.get_positive_current_limit()


		@api_server.app.get(f'/{self._uid}/get/lead_resistance', tags=[self._uid])
		async def get_lead_resistance() -> float:
			return self.get_lead_resistance()


		@api_server.app.get(f'/{self._uid}/get/magnet_inductance', tags=[self._uid])
		async def get_magnet_inductance() -> float:
			return self.get_magnet_inductance()


		@api_server.app.get(f'/{self._uid}/get/system_status', tags=[self._uid])
		async def get_system_status() -> SystemStatusMModel:
			return SystemStatusMModel[self.get_system_status().name]


		@api_server.app.get(f'/{self._uid}/get/limit_status', tags=[self._uid])
		async def get_limit_status() -> SystemStatusNModel:
			return SystemStatusNModel[self.get_limit_status().name]


		@api_server.app.get(f'/{self._uid}/get/activity_status', tags=[self._uid])
		async def get_activity_status() -> ActivityStatusModel:
			return ActivityStatusModel[self.get_activity_status().name]


		@api_server.app.get(f'/{self._uid}/get/remote_status', tags=[self._uid])
		async def get_remote_status() -> RemoteStatusModel:
			return RemoteStatusModel[self.get_remote_status().name]


		@api_server.app.get(f'/{self._uid}/get/heater_status', tags=[self._uid])
		async def get_switch_heater_status() -> SwitchHeaterStatusModel:
			return SwitchHeaterStatusModel[self.get_switch_heater_status().name]


		@api_server.app.get(f'/{self._uid}/get/sweep_mode_status', tags=[self._uid])
		async def get_sweep_mode_status() -> ModeStatusMModel:
			return ModeStatusMModel[self.get_sweep_mode_status().name]


		@api_server.app.get(f'/{self._uid}/get/sweep_status', tags=[self._uid])
		async def get_sweep_status() -> ModeStatusNModel:
			return ModeStatusNModel[self.get_sweep_status().name]



		@api_server.app.get(f'/{self._uid}/set/hold', tags=[self._uid])
		async def hold() -> int:
			self.hold()
			return 0


		@api_server.app.get(f'/{self._uid}/set/to_setpoint', tags=[self._uid])
		async def to_setpoint() -> int:
			self.to_setpoint()
			return 0


		@api_server.app.get(f'/{self._uid}/set/to_zero', tags=[self._uid])
		async def to_zero() -> int:
			self.to_zero()
			return 0


		@api_server.app.get(f'/{self._uid}/set/clamp', tags=[self._uid])
		async def clamp() -> int:
			self.clamp()
			return 0


		@api_server.app.get(f'/{self._uid}/set/heater_off', tags=[self._uid])
		async def heater_off() -> int:
			self.heater_off()
			return 0


		@api_server.app.get(f'/{self._uid}/set/heater_on', tags=[self._uid])
		async def heater_on() -> int:
			self.heater_on()
			return 0


		@api_server.app.get(f'/{self._uid}'+'/set/target_current/}', tags=[self._uid])
		async def set_target_current(current: float) -> int:
			self.set_target_current(current)
			return 0


		@api_server.app.get(f'/{self._uid}'+'/set/target_field/', tags=[self._uid])
		async def set_target_field(field: float) -> int:
			self.set_target_field(field)
			return 0


		@api_server.app.get(f'/{self._uid}'+'/set/current_sweep_rate/', tags=[self._uid])
		async def set_current_sweep_rate(rate: float) -> int:
			self.set_current_sweep_rate(rate)
			return 0


		@api_server.app.get(f'/{self._uid}'+'/set/field_sweep_rate/', tags=[self._uid])
		async def set_field_sweep_rate(rate: float) -> int:
			self.set_field_sweep_rate(rate)
			return 0
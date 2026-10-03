#!/usr/bin/env python3
"""Executable requirements model. NOT BSP, hardware control, or OTP configuration."""
from dataclasses import dataclass
from enum import Enum
class Mode(Enum):
    EMMC = 'emmc'
    TF = 'tf'
@dataclass(frozen=True)
class Policy:
    host_io_mv: int
    device_supply_mv: int
    device_signal_mv: int
    width: int
    maximum_target_hz: int
    hs200: bool
    uhs: bool
    nonremovable: bool
    card_ocr_mv_range: tuple[int,int]
def policy(mode: Mode) -> Policy:
    if mode is Mode.EMMC:
        return Policy(1800,3300,1800,8,200_000_000,True,False,True,(1700,1950))
    if mode is Mode.TF:
        return Policy(1800,3300,3300,4,50_000_000,False,False,False,(3200,3400))
    raise ValueError('Explicit cold build/assembly mode required')
def startup_permitted(*, qualification_link_fitted=False, otp_first_drive_verified=False,
                      power_and_reset_qualified=False, rom_media_protocol_verified=False,
                      assembly_mode=None, image_mode=None):
    # These are externally verified prerequisites, not sensed hardware inputs.
    return bool(qualification_link_fitted and otp_first_drive_verified and
                power_and_reset_qualified and rom_media_protocol_verified and isinstance(assembly_mode,Mode) and
                assembly_mode is image_mode)
if __name__ == '__main__':
    import itertools,json
    checks=0
    for mode in Mode:
        p=policy(mode)
        assert p.host_io_mv==1800 and p.device_supply_mv==3300
        assert not p.uhs
        assert p.card_ocr_mv_range==((1700,1950) if mode is Mode.EMMC else (3200,3400))
        checks+=4
    assert policy(Mode.TF).width==4 and not policy(Mode.TF).hs200
    assert policy(Mode.EMMC).width==8 and policy(Mode.EMMC).hs200
    checks+=4
    cases=0
    for q,o,r,m,a,i in itertools.product([False,True],repeat=6):
        am=Mode.TF if a else Mode.EMMC;im=Mode.TF if i else Mode.EMMC
        got=startup_permitted(qualification_link_fitted=q,otp_first_drive_verified=o,
            power_and_reset_qualified=r,rom_media_protocol_verified=m,assembly_mode=am,image_mode=im)
        assert got==(q and o and r and m and a==i)
        cases+=1
    assert not startup_permitted()
    print(json.dumps({'scope':'standalone requirements model; no device/register access',
      'policy_assertions':checks,'prerequisite_combinations':cases,'default_permitted':False,
      'not_tested':['BSP integration','BootROM/OTP','real card initialization','timing','hardware']},indent=2))

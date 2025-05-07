if 1:  # pragma: no cover
    from . import fAinslie as Ainslie
    from jDWM.fortran import jdwm_fort
    from jDWM import putilities

    CustomBaseModel = putilities.CustomBaseModel
    cart2offcentrecylindrical = putilities.cart2offcentrecylindrical
    masked_interpolation = putilities.masked_interpolation

    def wake_width(r, U):
        width = jdwm_fort.wake_width(r, U, len(r))
        return width

    def rotor_area_mean(r, x, rmax=1):
        return putilities.rotor_area_mean(r, x, rmax=rmax)

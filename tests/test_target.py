import pytest
import models

@pytest.mark.parametrize("ip, ports", [
    ("999.999.999.999", [80]),       # Unvalid IP Address
    ("niepoprawne_ip", [80]),        # Unvalid IP format
    ("127.0.0.1", [0]),              # Port 0 below accepted port range
    ("127.0.0.1", [65536]),          # Port 65536 above accepted port range
    ("127.0.0.1", "100-20"),         # Unvalid port range 
])
def test_target_invalid_inputs_raise_error(ip, ports):
    """Sprawdza, czy Target rzuca wyjątek dla błędnego IP, portów spoza zakresu i odwróconego zakresu."""
    with pytest.raises(ValueError):
        models.Target(ip, ports)

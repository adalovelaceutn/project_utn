import pytest

from kolb_profile_server.tools.teoria import get_profile_theory


def test_smoke() -> None:
    assert True


class TestGetProfileTheory:
    def test_returns_convergente_details(self) -> None:
        result = get_profile_theory("Convergente")

        assert result["nombre"] == "Convergente"
        assert result["formula"] == "CA + EA"
        assert "práctica" in result["descripcion"].lower() or "aplicaci" in result["descripcion"].lower()
        assert result["estrategia_agente"]
        assert "percepcion" in result["ejes"]
        assert "procesamiento" in result["ejes"]
        assert result["descripcion_modelo"]

    def test_case_insensitive(self) -> None:
        lower = get_profile_theory("divergente")
        upper = get_profile_theory("DIVERGENTE")
        mixed = get_profile_theory("Divergente")

        assert lower["nombre"] == upper["nombre"] == mixed["nombre"] == "Divergente"

    @pytest.mark.parametrize("style", ["Divergente", "Asimilador", "Convergente", "Acomodador"])
    def test_all_styles_return_complete_keys(self, style: str) -> None:
        result = get_profile_theory(style)

        for key in ("nombre", "formula", "descripcion", "estrategia_agente", "ejes", "descripcion_modelo"):
            assert key in result, f"Falta clave '{key}' para estilo '{style}'"

    def test_unknown_style_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="no reconocido"):
            get_profile_theory("Fantasma")

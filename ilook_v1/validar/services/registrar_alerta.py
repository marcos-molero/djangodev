from django.utils import timezone
from core.models import Ilh003


def registrar_alerta(tx, regla):
  """
  Graba las alertas generadas en el Ilh003.
  """
  Ilh003.objects.create(
        h003001=tx.lk1fil,
        h003002=tx.lk1can,
        h003003=tx.lk1mon,
        h003004=timezone.now().year,
        h003005=timezone.now().month,
        h003006=timezone.now().day,
        h003007=timezone.now().time(),
        h003008=regla.m006_alerta,
        h003009='1',  # Estatus activo
        h003010=tx.usuario_carga,
        h003011=timezone.now(),
        h003012=tx.lk1mto,
        h003013=tx.lk1tip_asiento,
        h003015=tx.lk1hor,
        h003016=tx.lk1ori,
        h003017=regla.m006_clase,
        h003018=tx.lk1ter,
        h003019=tx.lk1eva,
        h003020=tx.lk1prom,
        h003021=tx.lk1max,
        h003022=regla.m006_resultado,
        h003023=tx.lk1cod,
        h003024=tx.lk1nop,
        h003025=tx.lk1039,
        h003026=tx.lk1dno,
        h003027=tx.lk1038,
        h003028=tx.lk1022,
        h003029=tx.lk1per,
        h003033=tx.lk1com,
        h003034=tx.lk1nac,
        h003035=tx.lk1dni,
        h003036=tx.lk1041,
        h003037=tx.lk1mid,
        h003038=tx.lk1nri,
        h003039=tx.lk1pre,
        h003040=tx.lk1pap,
        h003041=regla.m006_sensibilidad,
        h003042=tx.lk1acu,
        h003043=tx.lk1cli,
        h003044=tx.lk1opc,
        h003046=tx.lk1seq,
        h003047=tx.lk1sal_ant,
        h003048=tx.lk1ia_pred,
        h003049=tx.lk1ia_clas
    )

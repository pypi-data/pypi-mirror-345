import asyncio
import os
import sys
from typing import List

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.schemas import Query
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

queries: List[Query] = [
    Query(
        query="¿De qué habla la quinta enmienda de la constitución?",
        role="Eres un abogado experto de harvard",
        display_in_console=True,
    ),
    Query(
        query="""
        ¿Cómo se detalla en el Artículo I, Sección 2 el mecanismo de asignación de representantes a
        los estados, y qué implicaciones podría tener la fórmula de prorrateo
        (incluyendo consideraciones como "las tres quintas partes" y la exclusión de indígenas)
        en términos de representación política y distribución de poder?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        El Artículo I, Sección 3 describe la organización y elección de senadores, incluyendo
        la división en tres clases. ¿Qué ventajas y desventajas podría presentar este sistema
        de renovación escalonada para la estabilidad y la continuidad de la representación estatal?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Basándote en el Artículo I, Sección 7, analiza el proceso legislativo que incluye la
        intervención del Presidente. ¿Cómo se equilibra el poder entre el Ejecutivo y
        el Congreso cuando se trata de la aprobación de leyes, y cuáles son las implicaciones
        del proceso de veto con objeciones detalladas?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        En el Artículo III se define el poder y la jurisdicción de la Corte Suprema.
        ¿Cuáles son las implicaciones de otorgar a la Corte Suprema jurisdicción
        original en casos que involucran a embajadores y estados, y cómo afecta esto
        el equilibrio entre poderes?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Con base en el Artículo II, analiza los límites impuestos al Presidente,
        especialmente en lo referente a la designación de funcionarios y la duración
        del mandato, y discute cómo estos límites buscan prevenir abusos de poder.
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Considerando las Enmiendas I al X (la Carta de Derechos), ¿cómo se aseguran y
        se limitan los poderes gubernamentales en relación con las libertades individuales,
        y qué desafíos se podrían plantear en la aplicación práctica de estos derechos?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        El Artículo V establece un mecanismo para modificar la Constitución.
        ¿Qué dificultades prácticas y políticas podrían derivarse de la necesidad de ratificar
        en tres cuartas partes de los estados, y cómo podría esto afectar la adaptabilidad de la
        Constitución a cambios sociales?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Analiza el Artículo IV en el contexto del principio de "plena fe y crédito".
        ¿Cómo se garantiza la uniformidad en el reconocimiento de leyes y registros judiciales
        entre estados, y qué problemas podría surgir en casos de discrepancias legales
        entre jurisdicciones?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        En la Sección 10 del Artículo I se imponen restricciones a los estados en términos de política
        exterior, emisión de moneda y tratados con naciones extranjeras.
        ¿Cómo se justifica constitucionalmente esta limitación y qué conflictos podría
        generar en la relación entre el gobierno federal y los estados?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Las Enmiendas del XIII al XXVII introducen cambios significativos en temas como la
        abolición de la esclavitud, el sufragio, y la limitación de mandatos presidenciales.
        ¿Cómo refleja esta evolución los cambios sociales y políticos en la historia de los Estados Unidos,
        y de qué manera impactan en la interpretación y aplicación de la Constitución original?
        """,
        display_in_console=True,
    ),
]


async def main():
    async with Session(type="standard", delete=True) as session:
        await session.ingest(input_dir=input_dir)
        await session.multiple_queries(queries=queries)


if __name__ == "__main__":
    asyncio.run(main())

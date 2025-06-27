import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.preprocessing import MultiLabelBinarizer

st.title('Analisis del uso de la inteligencia artificial en la comunidad Datanilo')
st.divider()
#leemos el dataframe con los resultaados de la encuesta
uso_ia = pd.read_excel(r'C:\Users\Dussand\Desktop\Finance Career\Uso_IA\Respuestas_Encuesta_IA.xlsx')

#eliminamos la marca temporal y la puntacion que no servirá para el analisis
uso_ia = uso_ia.drop(columns=['Marca temporal', 'Puntuación'], axis = 1)

#mostramos las columnas
columns = uso_ia.columns

#cambiamos el nombre de las columnas
renames = {
    columns[0]:'rango_edad',
    columns[1]:'ocupacion',
    columns[2]:'uso_diario',
    columns[3]:'frecuencia_uso',
    columns[4]:'herramientas_ia',
    columns[5]:'actividades_ia',
    columns[6]:'escala_productividad',
    columns[7]:'escala_dependencia',
    columns[8]:'escala_satisfaccion',
    columns[9]:'reemplazo_tareas',
    columns[10]:'recomendacion_ia',
    columns[11]:'confianza_ia'
}

uso_ia = uso_ia.rename(columns=renames)

#reemplazamos los valores de la columna uso diario a formato numerico
uso_ia['uso_diario'] = uso_ia['uso_diario'].replace({
    'Si': 0,
    'No': 1
})

uso_ia = uso_ia[uso_ia['uso_diario'] == 0]

#st.dataframe(uso_ia['frecuencia_uso'].unique())

trust_scale = uso_ia['confianza_ia'].mean()

uso_ia['confianza_ia'] = uso_ia['confianza_ia'].fillna(trust_scale)


# frecuencia_map = {
#     'Una vez a la semana o menos': 1,
#     'Varias veces a la semana': 2,
#     'Una vez al día': 3,
#     'Varias veces al día': 4
# }

# uso_ia['frecuencia_uso'] = uso_ia['frecuencia_uso'].replace(frecuencia_map)

# productividad_map  = {
#     'Nada': 1,
#     'Poco': 2,
#     'Sí, de forma moderada': 3,
#     'Sí, significativamente': 4
# }

# uso_ia['escala_productividad'] = uso_ia['escala_productividad'].replace(productividad_map)


# reemplazo_tareas  = {
#     'Ninguna': 1,
#     'Muy pocas': 2,
#     'Algunas': 3,
#     'Sí, muchas': 4
# }

# uso_ia['reemplazo_tareas'] = uso_ia['reemplazo_tareas'].replace(reemplazo_tareas)

# #reemplazamos los valores de la columna uso diario a formato numerico
# uso_ia['recomendacion_ia'] = uso_ia['recomendacion_ia'].replace({
#     'Si': 0,
#     'No': 1
# })


uso_ia.head()

#mostramos los valores unicos para el selectbox
opciones = ['Todos'] + uso_ia['ocupacion'].unique().tolist()

#analizaremos que rangos de edades usan mas las IA
ocupacion = uso_ia['ocupacion'].value_counts().reset_index(name='Cantidad'
)

#Contamos las cantidades de IA que se escogieron
uso_ia['cantidad_herramientas'] = uso_ia['herramientas_ia'].apply(
    lambda x: len(x.split(','))
)

#reemplazamos la opcion de todas las anteriores por todas las opciones mostradas
replace = '''Estudio, investigación, consultas académicas,
Trabajo (ofimática, desarrollo, creatividad, etc.),
Redacción de textos, correos o informes,
Generación de ideas o brainstorming,
Codificación o desarrollo de software,
Diseño gráfico o creación de contenido visual,
Tareas personales (recetas, viajes, decisiones, etc.),
Entretenimiento'''

#diccionario para el conteo de actividades
actividades_posibles = [
    "Estudio, investigación, consultas académicas",
    "Trabajo (ofimática, desarrollo, creatividad, etc.)",
    "Redacción de textos, correos o informes",
    "Generación de ideas o brainstorming",
    "Codificación o desarrollo de software",
    "Diseño gráfico o creación de contenido visual",
    "Tareas personales (recetas, viajes, decisiones, etc.)",
    "Entretenimiento"
]

uso_ia['actividades_ia'].replace('TODAS LAS ANTERIORES', replace.replace('\n', ' ').strip() , inplace=True)

def contar_actividades(celda):
    return sum(1 for act in actividades_posibles if act in celda)

for actividad in actividades_posibles:
    uso_ia[actividad] = uso_ia['actividades_ia'].apply(
        lambda x: 1 if actividad in x else 0
    )

uso_ia['contar_actividades'] = uso_ia['actividades_ia'].apply(contar_actividades)

st.write(f'Cantidad de encuestados {len(uso_ia)}')

# Paso 1: separar herramientas como lista
uso_ia['herramientas_lista'] = uso_ia['herramientas_ia'].apply(lambda x: [i.strip() for i in x.split(',')])

mlb = MultiLabelBinarizer()
herramientas_binarias = pd.DataFrame(mlb.fit_transform(uso_ia['herramientas_lista']),
                                     columns=mlb.classes_,
                                     index=uso_ia.index)

nombres_cortos = {
    'ChatGPT': 'ChatGPT',
    'Claude': 'Claude',
    'Deepseek': 'Deepseek',
    'Google Gemini (antes Bard)': 'Gemini',
    'Grok': 'Grok',
    'Microsoft Copilot': 'Copilot',
    'Midjourney / DALL·E (generación de imágenes)': 'Midjourney',
    'Notion AI': 'Notion',
    'Otras (especificar)': 'Otras',
    'Qwen': 'Qwen'
}

herramientas_binarias.rename(columns=nombres_cortos, inplace=True)

uso_ia = pd.concat([uso_ia.drop(columns=['herramientas_lista']), herramientas_binarias], axis=1)

uso_ia

fig = px.bar(
    ocupacion,
    x='ocupacion',
    y='Cantidad',
    text='Cantidad',
    title='Ocupaciones de los integrantes'

)
# Mostrar en Streamlit
st.plotly_chart(fig, use_container_width=True)
ocupacion['cantidad (%)'] = round(ocupacion['Cantidad'] / ocupacion['Cantidad'].sum() * 100, 2)

st.write(
    f'''
_Este grafico muestra que los {ocupacion['ocupacion'].values[0]} representan el mayor grupo de integrantes
del grupo con un {ocupacion['cantidad (%)'].values[0]}% del total, seguidos por los {ocupacion['ocupacion'].values[1]}
con un {ocupacion['cantidad (%)'].values[1]}% y finalmente {ocupacion['ocupacion'].values[2]} que representan
{ocupacion['cantidad (%)'].values[2]}%, siendo estos los grupos con mayor representacion en la comunidad._
'''
)

st.divider()

st.header('Analisis rango de edad por ocupacion')
st.write(
    '''
El presente análisis tiene como objetivo identificar cómo se distribuyen los rangos de edad dentro de cada grupo ocupacional (estudiantes, profesionales y emprendedores). Esta segmentación permite comprender qué generaciones están adoptando con mayor intensidad el uso de herramientas de inteligencia artificial, así como anticipar necesidades, comportamientos y niveles de familiaridad tecnológica asociados a cada perfil.

'''
)

c1, c2 = st.columns(2)



#mostramos los valores unicos para el selectbox
opciones = ['Todos'] + sorted(uso_ia['ocupacion'].unique().tolist())

with c1:
    #ahora si, utilizamos el selectbox
    filtrado_ocupacion = st.selectbox('Escoge una ocupacion', opciones) 
    if filtrado_ocupacion == 'Todos':
        uso_ia_filtrado = uso_ia
    else:
        uso_ia_filtrado = uso_ia[uso_ia['ocupacion'] == filtrado_ocupacion]
    
    rango_edad = uso_ia_filtrado['rango_edad'].value_counts().reset_index(name='Cantidad')
    rango_edad['cantidad (%)'] = round(rango_edad['Cantidad'] / rango_edad['Cantidad'].sum() * 100, 2)

    st.write(
            f'''
        _El rango de edad entre {rango_edad['rango_edad'].values[0]} años representa el {rango_edad['cantidad (%)'].values[0]}% de los integrantes dentro del grupo ocupacional de {filtrado_ocupacion}.
Este dato refleja la distribución de edad que domina en esta categoria de ocupacion, lo cual puede influir en el tipo de uso y nivel de adopción de herramientas de inteligencia artificial en ese contexto._
        '''
        )

with c2:

    fig = px.bar(
        rango_edad,
        x='rango_edad',
        y='Cantidad',
        text='Cantidad',
        title='Rango de edad de los integrantes'

    )
    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True, key='rango_edad')


actividades_perfil = uso_ia_filtrado.groupby('ocupacion').agg(
    cantidad_herramientas_promedio = ('cantidad_herramientas', 'mean'),
    contar_actividades_promedio = ('contar_actividades', 'mean'),
    frecuencia_uso_maxima = ('frecuencia_uso', 'max')
).reset_index().sort_values(by='contar_actividades_promedio', ascending=False)

st.divider()
st.header('¿Qué herramienta de IA es la mas utilizada por los encuestados de la comunidad.')
st.write(
        '''
    Analizaremos que herramientas de inteligencia artificial son las mas usadas por la comunidad, 
    y veremos que tan eficiente resulta para los usuarios.
'''
)

k1, k2 = st.columns(2)

with k1:
    #ahora si, utilizamos el selectbox
    filtrado_ocupacion_ia = st.selectbox('Escoge una ocupacion', opciones, key = 'ias') 
    
    if filtrado_ocupacion_ia == 'Todos':
        uso_ia_filtrado = uso_ia
    else:
        uso_ia_filtrado = uso_ia[uso_ia['ocupacion'] == filtrado_ocupacion_ia]
 
    ias_uso = uso_ia_filtrado[[
    'ChatGPT', 'Claude', 'Deepseek', 
    'Gemini', 'Grok',
    'Copilot', 'Midjourney',
    'Notion', 'Otras', 'Qwen'
]].sum().sort_values(ascending=False)
    
    ias_cols = ['ChatGPT', 'Claude', 'Deepseek', 'Gemini', 'Grok',
            'Copilot', 'Midjourney', 'Notion', 'Otras', 'Qwen']

    # # Diccionario para almacenar los resultados
    # ias_uso_efficiency = {}

    # # Calcular el promedio de productividad por cada IA
    # for ia in ias_cols:
    #     promedio = round(uso_ia_filtrado.loc[uso_ia_filtrado[ia] == 1, 'escala_productividad'].mean(), 2)
    #     ias_uso_efficiency[ia] = promedio

    # ias_uso_efficiency= pd.DataFrame.from_dict(ias_uso_efficiency, orient='index', columns=['productividad_promedio'])
    # ias_uso_efficiency
    ias_uso_df = ias_uso.reset_index()
    ias_uso_df.columns = ['IA', 'Cantidad']
    ias_uso_df['Cantidad (%)'] = round(ias_uso_df['Cantidad'] / ias_uso_df['Cantidad'].sum() * 100, 2) 
    # ias_uso_efficiency_df = ias_uso_efficiency.reset_index()
    # ias_uso_efficiency_df.columns = ['IA', 'Eficiencia']
    

    # ia_cant_eficiencia = pd.merge(ias_uso_df, ias_uso_efficiency_df, on='IA', how='inner' )
    # ia_cant_eficiencia
       
    if filtrado_ocupacion_ia == 'Todos':
        st.write(
            f'''

        De toda la comunidad, las tres herramientas de inteligencia artificial más utilizadas son:

        🥇 **{ias_uso_df['IA'].values[0]}**, con un **{ias_uso_df['Cantidad (%)'].values[0]}%** de preferencia   
        🥈 **{ias_uso_df['IA'].values[1]}**, con un **{ias_uso_df['Cantidad (%)'].values[1]}%**                          
        🥉 **{ias_uso_df['IA'].values[2]}**, con un **{ias_uso_df['Cantidad (%)'].values[2]}%**

        Este resultado refleja una clara inclinación hacia **{ias_uso_df['IA'].values[0]}** como la herramienta más popular entre los usuarios.
  

        '''
        )

    else:
               st.write(
            f'''
                Para la ocupacion de {filtrado_ocupacion_ia}, las tres herramientas de inteligencia artificial más utilizadas son:

        🥇 **{ias_uso_df['IA'].values[0]}**, con un **{ias_uso_df['Cantidad (%)'].values[0]}%** de preferencia  
        🥈 **{ias_uso_df['IA'].values[1]}**, con un **{ias_uso_df['Cantidad (%)'].values[1]}%**                    
        🥉 **{ias_uso_df['IA'].values[2]}**, con un **{ias_uso_df['Cantidad (%)'].values[2]}%** 

        Para esta ocupacion se puede apreciar una clara preferencia por **{ias_uso_df['IA'].values[0]}** como la herramienta más popular entre los usuarios de la categoría.
        '''
        )


with k2:

    fig = px.bar(
        ias_uso_df,
        x='Cantidad (%)',
        y='IA',
        text='Cantidad (%)',
        orientation='h',
        title='Uso de herramientas de IA por los integrantes del grupo'

    )

    # fig.update_traces(textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})  # IA más usada arriba
    # fig.show()
    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True, key='herr_ia')


st.write(
     f'''
En conclusión, hay una clara preferencia por ChatGPT dentro de la comunidad
, destacándose ampliamente por encima de otras herramientas. 
Su porcentaje de uso casi duplica al de la segunda opción, 
lo que evidencia su posicionamiento como la solución de inteligencia artificial más adoptada
 y confiable entre los usuarios.
'''
)

st.title('Análisis del Impacto y Adopción de IA en la Comunidad Usuaria')

st.write(
     '''
        En esta seccion analizaremos como la frecuencia, la cantidad de herramientas de IA, cantidad de actividades,
        la productividad, dependencia, satisfaccion y recomendacion, pueden influir en la decision de pagar la version
        plus de las IA's mas usadas.
'''
)

uso_ia_numerico = uso_ia[['ocupacion', 'frecuencia_uso', 'escala_productividad', 
                          'escala_dependencia', 'escala_satisfaccion', 'reemplazo_tareas', 
                          'recomendacion_ia', 'confianza_ia', 'cantidad_herramientas',
                          'contar_actividades', 'ChatGPT']]



selecciona_ia = st.selectbox('Selecciona una IA para calcular el porcentaje de viabilidad de compra del servicio plus:', ias_cols)


chat_gpt_uso = uso_ia[uso_ia[selecciona_ia] == 1]


#1. pregunta para la conclusion ¿Cuantos lo usan si quiera una vez al día?
st.subheader(f'Frecuencia de uso de {selecciona_ia}')
frecuencia_uso_porcentaje = chat_gpt_uso.groupby('frecuencia_uso')['frecuencia_uso'].count().reset_index(name='count')
frecuencia_uso_porcentaje['%'] = round(frecuencia_uso_porcentaje['count'] / frecuencia_uso_porcentaje['count'].sum() * 100,1)
st.dataframe(frecuencia_uso_porcentaje, use_container_width=True)

fig= px.bar(
    frecuencia_uso_porcentaje,
    x='frecuencia_uso',
    y='%',
    #color='Nivel',
    orientation='v',
    title=f'Distirbucion de niveles de frecuencia de uso de la {selecciona_ia}',
    color_discrete_sequence=px.colors.sequential.Viridis
)

fig.update_layout(
    barmode='stack',
    xaxis_tickformat='.0%',
    xaxis_title='Frecuencia de uso',
    yaxis_title='Porcentaje'
)

st.plotly_chart(fig, use_container_width=True, key='frecuencia_de_uso') 

porcentaje_sumado = round(frecuencia_uso_porcentaje[frecuencia_uso_porcentaje['frecuencia_uso'].isin(
     ['Varias veces al día', 'Varias veces a la semana']

)]['%'].sum(), 2)

##st.write(f'_El {frecuencia_uso_porcentaje['%'].values[2] + frecuencia_uso_porcentaje['%'].values[3]}% lo usa una vez al dia, o varias veces al dia_')
st.write(
     f'''
        _El {porcentaje_sumado:.2f}% de los usuarios reporta utilizar {selecciona_ia} al menos una vez al día, 
        ya sea una vez diaria o varias veces al día.
        Este dato evidencia un alto nivel de integración de la IA en las rutinas diarias 
        de trabajo o estudio, lo que sugiere que estas tecnologías están dejando de ser un recurso ocasional para convertirse en una herramienta habitual.
        Además, esta frecuencia de uso tan elevada puede estar correlacionada c
        con una percepción positiva de utilidad y productividad, lo que refuerza la necesidad de seguir fomentando
          el acceso, la capacitación y la adopción consciente de estas herramientas._


'''
)


#pregunta 2. ¿Cuantos perciben una alza en su productividad y cuanto es la escala de productividad promedio de los encuestados?
st.subheader('Percepcion de productividad')
escala_prod_porcentaje = chat_gpt_uso.groupby('escala_productividad')['escala_productividad'].count().reset_index(name='count')
escala_prod_porcentaje['%'] = round(escala_prod_porcentaje['count'] / escala_prod_porcentaje['count'].sum() * 100, 2)
st.dataframe(escala_prod_porcentaje, use_container_width=True)
escala_porcentaje__total = round(escala_prod_porcentaje[escala_prod_porcentaje['escala_productividad'].isin(
     ['Sí, de forma moderada', 'Sí, significativamente']

)]['%'].sum(), 2
)
fig= px.bar(
    escala_prod_porcentaje,
    x='escala_productividad',
    y='%',
    #color='Nivel',
    orientation='v',
    title=f'Distirbucion de niveles de productividad al usar {selecciona_ia}',
    color_discrete_sequence=px.colors.sequential.Viridis
)

fig.update_layout(
    barmode='stack',
    xaxis_tickformat='.0%',
    xaxis_title='Frecuencia de uso',
    yaxis_title='Porcentaje'
)

st.plotly_chart(fig, use_container_width=True, key='escala_productividad')

#escala_prod_mean = round(chat_gpt_uso['count'].mean(),2 )

# #st.write(f'Además de que se perciben en la comunidad que usa ChatGPT, una escala promedio de productividad de {escala_prod_mean}/5')
st.write(f'_El {escala_porcentaje__total:.2f}% de los encuestados indicó haber percibido una notoria mejora en su productividad tras utilizar herramientas de inteligencia artificial._')


#pregunta 3. ¿Que tan satisfechos estan?
st.subheader(f'Escala de satisfaccion con la {selecciona_ia}')
satisfaccion_mean = round(chat_gpt_uso['escala_satisfaccion'].mean(),2 ) * 100 / 5
st.write(f'_Con una puntuación promedio de {round(chat_gpt_uso['escala_satisfaccion'].mean(), 2)}/5, equivalente al {satisfaccion_mean:.1f}%, ChatGPT es percibido por la comunidad como una herramienta altamente satisfactoria_')

#pregunta 4. ¿Se reemplazan muchas o algunas tareas?
st.subheader(F'Reemplazo de tareas por {selecciona_ia}')
replace_task_porc = chat_gpt_uso.groupby('reemplazo_tareas')['reemplazo_tareas'].count().reset_index(name='count')
replace_task_porc['%'] = round(replace_task_porc['count'] / replace_task_porc['count'].sum() * 100, 2)

replace_task__total = replace_task_porc[replace_task_porc['reemplazo_tareas'].isin(
     ['Sí, muchas', 'Algunas']

)]['%'].sum()

st.dataframe(replace_task_porc, use_container_width=True)

fig= px.bar(
    replace_task_porc,
    x='reemplazo_tareas',
    y='%',
    #color='Nivel',
    orientation='v',
    title='Distirbucion de niveles de reemplazo de tareas',
    color_discrete_sequence=px.colors.sequential.Viridis
)

fig.update_layout(
    barmode='stack',
    xaxis_tickformat='.0%',
    xaxis_title='Frecuencia de uso',
    yaxis_title='Porcentaje'
)

st.plotly_chart(fig, use_container_width=True, key='reemplazo_tareas')

st.write(f"_Un **{replace_task__total:.2f}%** de los encuestados afirma que la IA ya está **automatizando parte significativa de sus tareas manuales habituales**_")

#pregunta 5. ¿Cuantos recomiendan usar IA?
st.subheader(f'Recomendacion de {selecciona_ia}')
recomend_ia = chat_gpt_uso.groupby('recomendacion_ia')['recomendacion_ia'].count().reset_index(name='count')
recomend_ia['%'] = round(recomend_ia['count'] / recomend_ia['count'].sum() * 100, 2)

recomend_ia_total = recomend_ia[recomend_ia['recomendacion_ia'].isin(['Si'])]['%'].sum()
st.dataframe(recomend_ia, use_container_width=True)


st.write(f"_El **{recomend_ia_total:.1f}%** recomienda activamente el uso de IA como apoyo diario, consolidándola como una herramienta cada vez más esencial._"
)


fig= px.bar(
    recomend_ia,
    x='recomendacion_ia',
    y='%',
    #color='Nivel',
    orientation='v',
    title=f'¿Se recomienda {selecciona_ia} al publico?',
    color_discrete_sequence=px.colors.sequential.Viridis
)

fig.update_layout(
    barmode='stack',
    xaxis_tickformat='.0%',
    xaxis_title='Frecuencia de uso',
    yaxis_title='Porcentaje'
)

st.plotly_chart(fig, use_container_width=True, key='recomendacion_ia')


#pregunta 6. ¿Que tan confiable es la IA para los encuestados de la comunidad?
st.subheader(f'Confiabilidad en el trabajo de la {selecciona_ia}')
confiable_ia = round(chat_gpt_uso['confianza_ia'].mean(),2 )
confiabilidad_ia_total = round(confiable_ia / 5 * 100, 2)
st.write(f'_Los encuestados otorgan una calificación de confianza promedio de **{confiable_ia:.2f}/5**, lo que representa un **{round(confiable_ia / 5 * 100, 2)}%** de confianza en el uso de inteligencia artificial._')

#pregunta 7. ¿Cuantas actividades en promedio se realizan usando IA?
st.subheader(f'Promedio de actividades que realizan los usuarios con {selecciona_ia}.')
actividades_ia = round(chat_gpt_uso['contar_actividades'].mean(),2 )
st.write(f'_En promedio cada usuario realiza con IA {actividades_ia} actividades._')


actividades_realizadas_ia = chat_gpt_uso[actividades_posibles].sum().sort_values(ascending=False)
actividades_realizadas_ia_df = actividades_realizadas_ia.reset_index()
actividades_realizadas_ia_df.columns = ['Actividades', 'Cantidad']

fig= px.bar(
    actividades_realizadas_ia_df,
    x='Cantidad',
    y='Actividades',
    #color='Nivel',
    orientation='h',
    title=f'Actividades mas realizadas con soporte de {selecciona_ia}',
    color_discrete_sequence=px.colors.sequential.Viridis
)

# fig.update_layout(
#     barmode='stack',
#     xaxis_tickformat='.0%',
#     xaxis_title='Frecuencia de uso',
#     yaxis_title='Porcentaje'
# )

st.plotly_chart(fig, use_container_width=True, key='actividades_realizadas_ia')
st.dataframe(actividades_realizadas_ia_df, use_container_width=True)
#st.dataframe(chat_gpt_uso)

st.title(f'¿Que tan confiable es pagar la version premium de {selecciona_ia}? ¿Vale la pena?')

st.write(

    f'''
Este análisis busca responder de forma objetiva si realmente conviene pagar por la versión Plus de {selecciona_ia}, 
a partir del comportamiento, percepción y recomendación de sus usuarios. 
Para ello, se recopilaron indicadores clave como frecuencia de uso, nivel de satisfacción, 
confianza, impacto en productividad, reemplazo de tareas y recomendación general.
Con el fin de construir un indicador global que resuma la intención y conveniencia de pago, 
se asignarán pesos a cada variable de manera subjetiva, permitiendo así capturar la importancia relativa que tiene cada una en la experiencia del usuario.
Esto dará lugar a un índice compuesto de recomendación, que podrá ser ajustado por cada usuario o analista según su criterio, brindando flexibilidad sin perder rigurosidad.

El resultado final será una métrica porcentual que indicará, 
con base en datos reales, qué tan recomendable y justificada es la decisión de pagar por la versión premium de {selecciona_ia}.
'''
)

# Valores reales de las métricas
metricas = {
    'Frecuencia de uso': porcentaje_sumado,
    'Percepción de productividad':escala_porcentaje__total,
    'Nivel de satisfacción': satisfaccion_mean,
    'Reemplazo de tareas': round(replace_task__total,2),
    'Recomendación de IA': recomend_ia_total,
    'Nivel de confianza': confiabilidad_ia_total
}

# Inicializar pesos por defecto
pesos_default = {
    'Frecuencia de uso': 15,
    'Percepción de productividad': 20,
    'Nivel de satisfacción': 15,
    'Reemplazo de tareas': 15,
    'Recomendación de IA': 20,
    'Nivel de confianza': 15
}

# Diccionario para guardar resultados
resultados = {}
pesos = {}

st.title("Cálculo del índice de recomendación para ChatGPT Plus")

st.markdown("Asigna los pesos a cada indicador (la suma debe ser 100%)")

# Mostrar métricas alineadas por fila
for nombre in metricas:
    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        st.metric(label=f"{nombre}", value=f"{metricas[nombre]}%")
    with col2:
        pesos[nombre] = st.slider(f"Peso - {nombre}", 0, 100, pesos_default[nombre], key=nombre)
    with col3:
        resultado = round(metricas[nombre] * pesos[nombre] / 100, 2)
        st.metric(label="Resultado", value=resultado)
        resultados[nombre] = resultado

# Validar pesos
suma_pesos = sum(pesos.values())
st.divider()
st.markdown(f"**Suma total de pesos:** {suma_pesos}%")

if suma_pesos != 100:
    st.warning("La suma de los pesos debe ser exactamente 100%. Ajusta los sliders.")
else:
    indice_total = sum(resultados.values())
    st.success(f"Índice final de recomendación: **{indice_total:.2f}%**")

    # Conclusión automática
    if indice_total >= 80:
        st.markdown(f"*Conclusión: Altamente recomendable considerar la versión Plus de {selecciona_ia}.*")
    elif 60 <= indice_total < 80:
        st.markdown(" *Conclusión: Podría ser útil si el uso es constante.*")
    else:
        st.markdown("*Conclusión: Aún no hay suficiente impacto para justificar el pago.*")



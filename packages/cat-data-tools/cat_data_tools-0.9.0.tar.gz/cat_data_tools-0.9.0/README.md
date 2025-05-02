# Cat data tools <a href="https://www.islas.org.mx/"><img src="https://www.islas.org.mx/img/logo.svg" align="right" width="256" /></a>

[![codecov](https://codecov.io/gh/IslasGECI/cat_data_tools/branch/develop/graph/badge.svg?token=MvLBzyGSH3)](https://codecov.io/gh/IslasGECI/cat_data_tools)
![licencia](https://img.shields.io/github/license/IslasGECI/cat_data_tools)
![languages](https://img.shields.io/github/languages/top/IslasGECI/cat_data_tools)
![commits](https://img.shields.io/github/commit-activity/y/IslasGECI/cat_data_tools)
![GitHub contributors](https://img.shields.io/github/contributors/IslasGECI/cat_data_tools)

## Overview

Python module with tools to process cat data.


# Adaptadores
Esta nota está inspirada en el tema de arquitectura hexagonal.
La necesidad nació de la petición de que nos hizo el equipo de trampeo por tener las coordenadas de las trampas con capturas.
En el estado actual no tenemos las coordenadas, pero nos hicieron llegar las coordenadas en un archivo GPX.
Ese archivo lo cambiamos a formato GeoJSON y de ahí a csv. 
La promesa es que ese archivo ya no nos lo van a mandar.
El próximo formato serán archivos de mapsource.

## ¿Qué hicimos?
Sabemos que las próximas coordenadas vendrán de un archivo distinto. 
Así que decidimos que un adaptador decida cómo generar el DataFrame a partir de diferentes fuentes de datos.
El adaptador nos regresará objetos que transforan de la fuente de datos a DataFrame.
El nombre del archivo fuente es el criterio para saber el tipo de objeto que nos entregará el DataFrame que necesitamos.

## ¿Dónde lo hicimos?
Trabajamos en el repositorio [`cat_data_tools`](https://github.com/IslasGECI/cat_data_tools). 
¿Cuál es el objetivo de este repositorio?
¿Dónde utilizamos este repositorio?
[Aquí](https://github.com/IslasGECI/cat_data_tools/blob/develop/cat_data_tools/adapters.py) podemos ver la implementación.

## ¿Qué hace el adaptador?
La función `Adapter_for_path_to_dataframe()` nos entrega un objeto del tipo `Adapter_from_path` (creo que podemos mejorar el nombre. Tal vez transformer en lugar de adapter).
Estos objetos tienen un método `get_dataframe()` encargado de entregar el DataFrame con las columnas correctas.
La única razón para cambiar a la función `Adapter_for_path_to_dataframe()` es que agreguemos a una clase "`transformer`" nueva.
Las clases `transformer` cambian de manera independiente, cada una dependen del archivo con el que las inicializamos.
La razón por la que podrían cambiar todas las clases `transformer` es que las columnas de salida cambien de nombre.  

## ¿Qué logramos?
El cambio que nos prometieron que vendría lo tenemos encapsulado.
Cuando la fuente de datos sea distinta tenemos que escribir una nueva clase que cumpla con la misma interfaz. ¿Podemos decir lo mismo sin usar la palabra interfaz?
Además tendremos que agregar un opción en el diccionario [`choice`](https://github.com/IslasGECI/cat_data_tools/blob/develop/cat_data_tools/adapters.py#L6).

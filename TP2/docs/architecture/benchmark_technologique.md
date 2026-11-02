Para o dataset temos:

17 combinações possiveis.


Abordagens para a classificação:

A - Classificação por combinação: 17 classes, inutil para bombons que nao estao no treinamento

B - Dois modelos independentes 
    Modelo 1: Para o TIPO
    Modelo 2: Para a cor

C -  Multi-Task Learning
    Image -> CNN Backbone -> Feature Extraction -> Classification du type et classification de la couleur


Para o DATASET

| Parâmetro | Variação |
|---|---|
| Position | Centro, esquerda, direita |
| Rotation | Diferentes orientações |
| Distance | Próximo e distante |
| Luminosité | Diferentes intensidades |
| Angle | Vista superior e pequenas inclinações |
| Objet physique | Diferentes exemplares da mesma variante |


2. Protocole d'acquisition des images

2.1. Quantidade de fotografias

Como nosso dataset possui 17 variantes, proponho inicialmente 15 fotografias por variante, totalizando 255 fotos Esse será nosso dataset pilote, utilizado para validar o processo de aquisição, anotação e treinamento. Posteriormente, poderemos ampliar a base para aproximadamente 60 a 100 fotografias por variante, dependendo dos resultados.

2.2. Diversidade das imagens

Característica	Variações propostas

Orientation	0°, 45°, 90°, 180°
Position	Centro, esquerda, direita
Distance	Próximo, intermediário, distante
Éclairage	Natural e artificial
Angle de vue	Superior e inclinado
Exemplaire	Diferentes unidades do mesmo doce


Importante: essas variações devem ser realizadas durante a aquisição das imagens. Posteriormente, utilizaremos técnicas de Data Augmentation para ampliar a diversidade durante o treinamento.



2.3. Sessões de aquisição

Recomendo dividir inicialmente as 15 fotografias de cada variante em três sessões:
Sessão	Fotografias	            Condições
S01	        5	        Iluminação uniforme, vista superior
S02	        5	        Diferentes posições e orientações
S03	        5	        Iluminação e ângulos diferentes

# uniconpy

Pacote Python para conversão de unidades de medida, como temperatura, área e volume. Desenvolvido com foco em aplicações educacionais e computacionais, o pacote oferece funções simples e intuitivas para uso em projetos científicos, acadêmicos ou do dia a dia.

  

## Instalação

Você pode instalar o pacote diretamente do PyPI com o seguinte comando:

```python
pip install conversao_unidades
```

Caso esteja desenvolvendo localmente, é possível instalar utilizando:

```python
pip install .
```

  

## Exemplos de Uso

```python

import uniconpy as uc

#Conversão de temperatura
print(uc.temperatura.celsius_para_fahrenheit(25)) # Saída: 77.0

#Conversão de área
print(area.metros_quadrados_para_hectares(10000)) # Saída: 1.0

#Conversão de volume
print(volume.litros_para_metros_cubicos(1000)) # Saída: 1.0
```

## Documentação

A documentação completa, incluindo tutoriais e instruções detalhadas, está disponível no diretório `docs/`:

  

## Requisitos

- Python >= 3.8

- Nenhuma dependência externa

  

## Licença

Distribuído sob a licença MIT. Isso significa que você pode utilizar, modificar e distribuir o pacote livremente, desde que mantenha os créditos ao autor original. Para mais informações, consulte o arquivo [LICENSE.txt](LICENSE.txt).

  

## Contato

Autor: Matcomp

Email: projeto@matcomp.com.br

  

**Obs:** Projeto desenvolvido como parte do curso "Criação de Pacotes em Python"

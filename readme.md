# Desenvolvendo uma API com a AWS Educate
## Dados sobre Ocorrências Criminais, SINESP - Ministério da Justiça obtidos pelo link:
### http://dados.gov.br/dataset/sistema-nacional-de-estatisticas-de-seguranca-publica

# Instalação

## 1 - Crie uma nova instância EC2 **Ubuntu** na AWS Educate, segue um tutorial de como criar uma instância na AWS: https://www.youtube.com/watch?v=4kufR3fFEjM

## 2 - Instale o Putty em seu computador para acessar sua instância EC2 utilizando o IP público do mesmo.
### 2.1 - Utilize o Putty para converter sua chave .pem para .ppk como mostrado no tutorial: https://medium.com/@praneeth.jm/launching-and-connecting-to-an-aws-ec2-instance-6678f660bbe6

## 3 - Execute a sequência de comandos abaixo no terminal da sua instância pelo Putty:
### 3.1 - Baixe o script de configuração do ambiente.
<code>wget https://raw.githubusercontent.com/SamuelHericles/Desenvolvendo_uma_API/master/02.C%C3%B3digos/configAPI.sh</code>

### 3.2 -  Conceda permissões de leitura e escrita ao script de configuração.
<code>sudo chmod 777 configAPI.sh</code>

### 3.3 - Execute-o.
<code>./configAPI.sh</code>

# Funcionamento

## Em construção ...


## #Equipe4 - Ciência de Dados - Desenvolvendo uma Nova API

Feito com 💙 e Python
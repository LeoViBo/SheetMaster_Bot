# SheetMaster_Bot

Um bot do Discord usado para acompanhar informações de seu personagem de DnD 5e.
Ele permite para que cada jogador crie e controle sua ficha de personagem, rode dados e acompenha o HP diretamente do Discord.

[Clique aqui para adicionar o SheetMaster_Bot no seu servidor](https://discord.com/oauth2/authorize?client_id=1494781903524331540&permissions=8&integration_type=0&scope=bot)

---

## Requisitos

- Python 3.10 ou superior
- A aplicação do discord e um token do discord que consegue pegar aqui [Discord Developer Portal](https://discord.com/developers/applications)
- O ID do servidor de onde o bot vai ser usado (utilizado para fazer o bot iniciar mais rapidamente ao invez tentar puxar automaticamente)

´PS: qualquer dúvida sobre ID do servidor ou o Token do discord são fácilmente encontradas com uma pesquisa no google

---

## Instalação

1. Clone o repositório [SheetMaster_Bot repository](https://github.com/LeoViBo/SheetMaster_Bot)

2. Instale as dependências no terminal:

```bash
pip install -r requirements.txt
```

3. Crie um arquivo '.env' na root do projeto com seguinte conteúdo (subtitua os valores respectivos)

```
DISCORD_TOKEN=your_token_here
SERVER_ID=your_server_id_here
```

4. Rode a aplicação main.py - O bot vai funcionar enquanto a aplicação estiver rodando

---

## Project Structure

```
SheetMaster_bot/
├── main.py             # Arquivo de inicialização
├── requirements.txt    # Dependencias do projeto
├── README.md           # Esse arquivo
├── discord.log         # log com detalhes da ultima vez que a aplicação foi rodada
├── .env                # Token e ID do servidor (Feitos manualmente)
├── .gitignore          # Arquivos que o Git deve ignorar
├── data/
│   └── data.json       # Armazenamento de dados dos personagens
└── cogs/
    └── Dnd5eSheet.py   # Todos os comandos do Bot
```

---

## Comandos

### Sheet

| Comandos        | Descrição                                                                                                |
|-----------------|----------------------------------------------------------------------------------------------------------|
| `/create_sheet` | Cria um personagem atrelado ao seu ID. Tem alguns campos que é preciso preencher para criar o personagem |
| `/show_sheet`   | Mostra uma mensagem embed com todas as informações do seu personagem                                     |
| `/delete_sheet` | Deleta permanentemente seu personagem                                                                    |

### Set

| Comandos            | Descrição                                                                            |
|---------------------|--------------------------------------------------------------------------------------|
| `/set_atribute`     | Atualiza um dos seus seis atributos (STR, DEX, CON, INT, WIS, CHA)                   |
| `/set_combat`       | Atualiza a Armadura, iniciativa ou velociadade do personagem                         |
| `/give_proficiency` | Ativa/desativa a proficiencia de uma skill ou saving throw                           |
| `/add_item`         | Adiciona uma nova entrada nas habilidades, traços, invetário ou outras proficiencias |
| `/remove_item`      | Remove uma nova entrada nas habilidades, traços, invetário ou outras proficiencias   |

### Dice

| Comandos            | Descrição                                                                                                                                                    |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/roll_skill`       | Rola 1d20 com modificador de atributo ou de alguma skill                                                                                                     |
| `/roll_initiative`  | Rola iniciativa usando seu bonus de iniciativa                                                                                                               |
| `/roll_combat`      | Rola qualquer quantidade de dado de quantas faces o jogador quiser e faz com que botões apareçam para aplciar o valor a vida do usuario de diferentes formas |
| `/roll_death_save`  | Rola 1d20 para fazer teste de morte                                                                                                                          |
| `/reset_death_save` | Reseta os valores do teste de morte                                                                                                                          |


---

## Como funciona

Cada usuario do servidor pode ter apenas um ficha que será salvo no `data/data.json`  
A ficha guarda as principais informações de um personagem de DnD 5e:  
- Attributes (Atributos);  
- Skills (Habilidades);  
- Saving throws (Teste de resitência);  
- HP (Pontos de Vida);  
- Death Saves (Testes de morte);  
- Armor Class (Armadura);  
- Speed (Velocidade);  
- Initiative (Iniciativa);  
- Inventory (Intentário);  
- Abilities (Habilidades);  
- Traits (Traços);  
- Proficiencies (Proficiências);  

Habilidades e testes de resitência são calculado automativamente sempre que um atributo é alterado.  
O comando `/roll_combat` rola o dado e apresenta botões interativos que para aplicar o valor rodado de formas diferentes no HP do personagem de quem clicar no botão.  

---

## Notas

- Os comandos só funcinam dentro do servidor com definido no `SERVER_ID`. Isso foi feito intensionalmente para poder fazer o bot iniciar a rodar mais rapidamente.
- Peronsagens são armazenados entre sessões dentro do `data.json`. Mas cada personagem é atribuido a um servidor.
- Para simplicidade inicial cada usuario pode ter apenas um personagem ativo.

# Implementação de Imagens de Capa para Hotéis com MongoDB

## Resumo das Alterações

Foi implementada a funcionalidade de upload e exibição de imagens de capa para hotéis usando MongoDB como armazenamento.

## Mudanças Realizadas

### 1. **pacotes/forms.py**
- Adicionado campo `imagem` ao `HotelForm` para permitir upload de imagens
- Campo configurado como `ImageField` opcional com widget personalizado

### 2. **pacotes/views.py**

#### Configuração MongoDB
- Adicionada referência à collection `capa_hotel` do MongoDB

#### Função `hotel()`
- Atualizada para processar `request.FILES`
- Salva a imagem no MongoDB quando um hotel é criado
- Estrutura de dados no MongoDB:
  ```python
  {
      'hotel_id': int,
      'nome_hotel': str,
      'imagem': binary,
      'content_type': str,
      'filename': str
  }
  ```

#### Função `editar_hotel()`
- Atualizada para processar upload de novas imagens
- Atualiza ou insere imagem no MongoDB usando `upsert=True`

#### Função `reserva_pacote()`
- Modificada para buscar informações de imagens do MongoDB
- Passa para o template uma lista de dicionários com informação sobre se o hotel tem imagem

#### Nova Função `hotel_imagem()`
- Serve as imagens armazenadas no MongoDB
- Retorna a imagem com o content-type correto
- Levanta Http404 se a imagem não for encontrada

#### Função `eliminar_hotel()`
- Atualizada para eliminar a imagem do MongoDB antes de eliminar o hotel
- Garante que não ficam imagens órfãs no MongoDB

### 3. **pacotes/urls.py**
- Adicionada nova rota: `path("hoteis/<int:hotel_id>/imagem/", views.hotel_imagem, name="hotel_imagem")`

### 4. **pacotes/templates/reserva_pacote.html**
- Atualizado para usar a URL da nova view `hotel_imagem`
- Exibe placeholder quando não há imagem disponível
- Usa `{% url 'hotel_imagem' hotel.hotel_id %}` para buscar a imagem do MongoDB

### 5. **main/templates/hoteis.html**
- Adicionado `enctype="multipart/form-data"` ao formulário para suportar upload de arquivos

## Como Usar

### Adicionar Imagem ao Criar Hotel
1. Acesse a página de gestão de hotéis
2. Preencha os dados do hotel
3. Selecione a imagem de capa no campo "Imagem de Capa do Hotel"
4. Clique em "Guardar Hotel"

### Adicionar/Atualizar Imagem de Hotel Existente
1. Acesse a página de gestão de hotéis
2. Clique em "Editar" no hotel desejado
3. Selecione uma nova imagem
4. Clique em "Guardar Alterações"

### Visualizar Imagens na Escolha de Hotel
1. Ao reservar um pacote, a página de escolha de hotel irá exibir:
   - A imagem de capa do hotel (se disponível no MongoDB)
   - Um placeholder genérico (se não houver imagem)

## Estrutura MongoDB

### Collection: `capa_hotel`

```javascript
{
    "_id": ObjectId("..."),
    "hotel_id": 1,
    "nome_hotel": "Hotel Palma",
    "imagem": BinData(...),
    "content_type": "image/jpeg",
    "filename": "hotel_palma.jpg"
}
```

## Vantagens desta Implementação

1. **Separação de Responsabilidades**: Dados estruturados no PostgreSQL, imagens no MongoDB
2. **Escalabilidade**: MongoDB é otimizado para armazenamento de arquivos binários
3. **Flexibilidade**: Fácil adicionar metadados às imagens no futuro
4. **Performance**: Imagens servidas diretamente do MongoDB sem processamento intermediário

## Notas Técnicas

- As imagens são armazenadas como dados binários (binary data) no MongoDB
- O `content_type` é preservado para servir a imagem corretamente no navegador
- Usa-se `upsert=True` para facilitar tanto inserção quanto atualização
- A view `hotel_imagem` retorna `HttpResponse` com a imagem e content-type apropriado

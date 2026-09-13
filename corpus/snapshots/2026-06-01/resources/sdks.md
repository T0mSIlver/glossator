---
url: https://docs.mistral.ai/resources/sdks
title: SDKs
breadcrumbs: [Resources]
kind: doc
locale: en
source_path: src/content/en/docs/resources/sdks/page.mdx
source_commit: de827c0ffd57e13bd3b026e3669c455ee2532b82
---

# SDK Clients

SDK Clients allow you to interact with Mistral AI's API in your preferred programming language, they implement clean and simple interfaces to our API endpoints and services.
We strongly recommend using the official SDKs to interact with our APIs.

## SDKs {#sdks}

We provide official SDK clients in both Python and Typescript, you can also find third-party non-official SDKs in other languages.

**Python SDK**

You can install our [Python Client](https://github.com/mistralai/client-python) by running:

**Bash**

```bash
pip install mistralai
```

Once installed, you can for example run the chat completion as follows:

**Python**

**V1**

```python
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-medium-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model = model,
    messages = [
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ]
)
```

**V2**

```python
import os
from mistralai.client import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-medium-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model = model,
    messages = [
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ]
)
```

**Output**

```json
{
  "id": "7c163b08d98e4eebb35564ae14ffe6e4",
  "created": 1756130273,
  "model": "mistral-medium-latest",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 1160,
    "completion_tokens": 1150
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "tool_calls": null,
        "content": "The \"best\" French cheese is highly subjective—it depends on personal taste, texture preferences, and how you plan to enjoy it (on a cheese board, melted, in cooking, etc.). However, here are some of the most **iconic, beloved, and award-winning French cheeses**, each celebrated for its unique qualities:\n\n### **Top Contenders for \"Best\" French Cheese**\n1. **Comté** (AOP)\n   - **Why?** A versatile, nutty, and complex **alpine cheese** aged 4 months to 3+ years. Younger Comté is mild and buttery; aged versions develop crystalline crunch and deep caramelized flavors.\n   - **Best for:** Cheese boards, fondue, grilled cheese, or eating plain.\n   - **Fun fact:** Made in the Jura Mountains, each wheel is unique based on the terroir and aging.\n\n2. **Roquefort** (AOP)\n   - **Why?** The **king of blue cheeses**, made from sheep’s milk and aged in natural caves. Creamy, tangy, and intensely flavorful with a sharp, salty bite.\n   - **Best for:** Spread on bread with honey or pears, in salads, or sauces.\n   - **Fun fact:** One of the oldest cheeses in France (mentioned by Pliny the Elder in 79 AD).\n\n3. **Camembert de Normandie** (AOP)\n   - **Why?** The **quintessential French cheese**—creamy, earthy, and slightly mushroomy when ripe. Invented in 1791 by Marie Harel.\n   - **Best for:** Baked (Camembert en croûte), with crusty bread, or apples.\n   - **Pro tip:** Eat it at room temperature when the center is soft but not runny.\n\n4. **Époisses de Bourgogne** (AOP)\n   - **Why?** A **pungent, washed-rind cheese** with a velvety texture and bold, barnyardy flavor. Napoleon reportedly loved it.\n   - **Best for:** Spreading on bread or pairing with Burgundy wine.\n   - **Warning:** So strong it’s banned on French public transport!\n\n5. **Reblochon** (AOP)\n   - **Why?** The **star of tartiflette**—creamy, nutty, and slightly smoky. Made in the Alps with raw cow’s milk.\n   - **Best for:** Melting in tartiflette, raclette, or on potatoes.\n\n6. **Brie de Meaux** (AOP)\n   - **Why?** The **\"King of Cheeses\"** (as declared at the 1815 Congress of Vienna). Rich, buttery, and mushroomy with a soft rind.\n   - **Best for:** Pairing with Champagne or fruit (grapes, figs).\n\n7. **Munster (Munster-Géromé)** (AOP)\n   - **Why?** A **stinky, washed-rind cheese** from Alsace with a creamy, tangy interior. Often served with cumin.\n   - **Best for:** Melting in tarts or eating with beer.\n\n8. **Beaufort** (AOP)\n   - **Why?** A **firm, nutty alpine cheese** similar to Gruyère but richer. Aged versions are caramelized and complex.\n   - **Best for:** Fondue, gratins, or shaving over salads.\n\n9. **Pélardon** (AOP)\n   - **Why?** A **small, tangy goat cheese** from the Cévennes or Provence. Comes in fresh (soft) or aged (firm, peppery) varieties.\n   - **Best for:** Salads, tartines, or grilled with herbs.\n\n10. **Bleu d’Auvergne** (AOP)\n   - **Why?** A **creamy, spicy blue cheese** with a sharper taste than Roquefort but less crumbly.\n   - **Best for:** Dressings, burgers, or cheese plates with walnuts.\n\n### **How to Choose?**\n- **Mild & creamy?** → Brie de Meaux, Camembert, Saint-André.\n- **Bold & stinky?** → Époisses, Munster, Pont-l’Évêque.\n- **Nutty & firm?** → Comté, Beaufort, Cantal.\n- **Blue cheese lover?** → Roquefort, Bleu d’Auvergne.\n- **Goat cheese fan?** → Crottin de Chavignol, Pélardon, Valençay.\n\n### **Pro Tips for Enjoying French Cheese**\n- **Serve at room temperature** (take it out of the fridge 1–2 hours before eating).\n- **Pair with wine**: Brie + Champagne, Roquefort + Sauternes, Comté + Jura wine.\n- **Avoid plastic wrap**—store in cheese paper or a breathable container.\n- **Visit a *fromagerie*** in France for expert recommendations!\n\n### **Final Verdict**\nIf forced to pick **one \"best\"**, **Comté** (aged 24+ months) and **Roquefort** are often crowned for their depth and versatility. But the true joy of French cheese is in the **diversity**—so try them all!\n\n**What’s your favorite?** 😊🧀"
      }
    }
  ]
}
```

See more examples [here](https://github.com/mistralai/client-python/tree/main/examples).

**Typescript SDK**

You can install our [Typescript Client](https://github.com/mistralai/client-ts) in your project using:

**Bash**

```bash
npm install @mistralai/mistralai
```

Once installed, you can run the chat completion:

**TypeScript**

```typescript
import { Mistral } from '@mistralai/mistralai';

const apiKey = process.env.MISTRAL_API_KEY || 'your_api_key';

const client = new Mistral({apiKey: apiKey});

const chatResponse = await client.chat.complete({
  model: 'mistral-medium-latest',
  messages: [{role: 'user', content: 'What is the best French cheese?'}],
});
```

**Output**

```json
{
  "id": "7c163b08d98e4eebb35564ae14ffe6e4",
  "created": 1756130273,
  "model": "mistral-medium-latest",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 1160,
    "completion_tokens": 1150
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "tool_calls": null,
        "content": "The \"best\" French cheese is highly subjective—it depends on personal taste, texture preferences, and how you plan to enjoy it (on a cheese board, melted, in cooking, etc.). However, here are some of the most **iconic, beloved, and award-winning French cheeses**, each celebrated for its unique qualities:\n\n### **Top Contenders for \"Best\" French Cheese**\n1. **Comté** (AOP)\n   - **Why?** A versatile, nutty, and complex **alpine cheese** aged 4 months to 3+ years. Younger Comté is mild and buttery; aged versions develop crystalline crunch and deep caramelized flavors.\n   - **Best for:** Cheese boards, fondue, grilled cheese, or eating plain.\n   - **Fun fact:** Made in the Jura Mountains, each wheel is unique based on the terroir and aging.\n\n2. **Roquefort** (AOP)\n   - **Why?** The **king of blue cheeses**, made from sheep’s milk and aged in natural caves. Creamy, tangy, and intensely flavorful with a sharp, salty bite.\n   - **Best for:** Spread on bread with honey or pears, in salads, or sauces.\n   - **Fun fact:** One of the oldest cheeses in France (mentioned by Pliny the Elder in 79 AD).\n\n3. **Camembert de Normandie** (AOP)\n   - **Why?** The **quintessential French cheese**—creamy, earthy, and slightly mushroomy when ripe. Invented in 1791 by Marie Harel.\n   - **Best for:** Baked (Camembert en croûte), with crusty bread, or apples.\n   - **Pro tip:** Eat it at room temperature when the center is soft but not runny.\n\n4. **Époisses de Bourgogne** (AOP)\n   - **Why?** A **pungent, washed-rind cheese** with a velvety texture and bold, barnyardy flavor. Napoleon reportedly loved it.\n   - **Best for:** Spreading on bread or pairing with Burgundy wine.\n   - **Warning:** So strong it’s banned on French public transport!\n\n5. **Reblochon** (AOP)\n   - **Why?** The **star of tartiflette**—creamy, nutty, and slightly smoky. Made in the Alps with raw cow’s milk.\n   - **Best for:** Melting in tartiflette, raclette, or on potatoes.\n\n6. **Brie de Meaux** (AOP)\n   - **Why?** The **\"King of Cheeses\"** (as declared at the 1815 Congress of Vienna). Rich, buttery, and mushroomy with a soft rind.\n   - **Best for:** Pairing with Champagne or fruit (grapes, figs).\n\n7. **Munster (Munster-Géromé)** (AOP)\n   - **Why?** A **stinky, washed-rind cheese** from Alsace with a creamy, tangy interior. Often served with cumin.\n   - **Best for:** Melting in tarts or eating with beer.\n\n8. **Beaufort** (AOP)\n   - **Why?** A **firm, nutty alpine cheese** similar to Gruyère but richer. Aged versions are caramelized and complex.\n   - **Best for:** Fondue, gratins, or shaving over salads.\n\n9. **Pélardon** (AOP)\n   - **Why?** A **small, tangy goat cheese** from the Cévennes or Provence. Comes in fresh (soft) or aged (firm, peppery) varieties.\n   - **Best for:** Salads, tartines, or grilled with herbs.\n\n10. **Bleu d’Auvergne** (AOP)\n   - **Why?** A **creamy, spicy blue cheese** with a sharper taste than Roquefort but less crumbly.\n   - **Best for:** Dressings, burgers, or cheese plates with walnuts.\n\n### **How to Choose?**\n- **Mild & creamy?** → Brie de Meaux, Camembert, Saint-André.\n- **Bold & stinky?** → Époisses, Munster, Pont-l’Évêque.\n- **Nutty & firm?** → Comté, Beaufort, Cantal.\n- **Blue cheese lover?** → Roquefort, Bleu d’Auvergne.\n- **Goat cheese fan?** → Crottin de Chavignol, Pélardon, Valençay.\n\n### **Pro Tips for Enjoying French Cheese**\n- **Serve at room temperature** (take it out of the fridge 1–2 hours before eating).\n- **Pair with wine**: Brie + Champagne, Roquefort + Sauternes, Comté + Jura wine.\n- **Avoid plastic wrap**—store in cheese paper or a breathable container.\n- **Visit a *fromagerie*** in France for expert recommendations!\n\n### **Final Verdict**\nIf forced to pick **one \"best\"**, **Comté** (aged 24+ months) and **Roquefort** are often crowned for their depth and versatility. But the true joy of French cheese is in the **diversity**—so try them all!\n\n**What’s your favorite?** 😊🧀"
      }
    }
  ]
}
```

See more examples [here](https://github.com/mistralai/client-js/tree/main/examples).

**Third-party SDKs**

Here are some **clients built by the community** for various other languages:

This section lists third-party clients in other languages provided by the community.
Please note that these clients are not actively maintained or supported by Mistral AI.
We recommend reaching out to the respective maintainers for any assistance or inquiries.

| Language       | Repository Links                                                                 |      |
|----------------|----------------------------------------------------------------------------------|------|
| CLI            | https://github.com/icebaker/ruby-nano-bots                 |      |
| Dart           | https://github.com/nomtek/mistralai_client_dart  |      |
| Elixir         | https://github.com/axonzeta/mistral_elixir            |      |
| Go             | https://github.com/Gage-Technologies/mistral-go  |      |
| Java           | https://github.com/langchain4j/langchain4j | https://github.com/spring-projects/spring-ai|
| JavaScript/TS  | https://github.com/vercel/ai                                    |      |
| PHP            | https://github.com/HelgeSverre/mistral | https://github.com/partITech/php-mistral |
| Ruby           | https://github.com/gbaptista/mistral-ai | https://github.com/wilsonsilva/mistral |
| Rust           | https://github.com/ivangabriele/mistralai-client-rs ||

{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 88,
   "id": "4118c85f-9a40-47b9-a64a-d1dc88f2d428",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "🛒 Product Recommendation System \n"
     ]
    },
    {
     "name": "stdin",
     "output_type": "stream",
     "text": [
      "Enter your preference (e.g., phone under $500):  phone under $700\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "Recommendation Result:\n",
      "[{'id': 2, 'name': 'Samsung Galaxy A54', 'price': 449, 'category': 'phone', 'link': 'https://www.samsung.com/galaxy-a54/'}, {'id': 3, 'name': 'Google Pixel 7', 'price': 599, 'category': 'phone', 'link': 'https://store.google.com/product/pixel_7'}]\n"
     ]
    }
   ],
   "source": [
    "import json\n",
    "import os\n",
    "import re\n",
    "from openai import OpenAI, OpenAIError\n",
    "\n",
    "# ----------------------------------\n",
    "# CONFIG\n",
    "# ----------------------------------\n",
    "api_key = os.getenv(\"OPENAI_API_KEY\",\n",
    "                    \"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\")\n",
    "\n",
    "client = OpenAI(api_key=api_key)\n",
    "\n",
    "# ----------------------------------\n",
    "# PRODUCT CATALOG\n",
    "# ----------------------------------\n",
    "products = [\n",
    "    {\"id\": 1, \"name\": \"iPhone 14\", \"price\": 799, \"category\": \"phone\", \"link\": \"https://www.apple.com/iphone-14/\"},\n",
    "    {\"id\": 2, \"name\": \"Samsung Galaxy A54\", \"price\": 449, \"category\": \"phone\", \"link\": \"https://www.samsung.com/galaxy-a54/\"},\n",
    "    {\"id\": 3, \"name\": \"Google Pixel 7\", \"price\": 599, \"category\": \"phone\", \"link\": \"https://store.google.com/product/pixel_7\"},\n",
    "    {\"id\": 4, \"name\": \"MacBook Air M2\", \"price\": 1199, \"category\": \"laptop\", \"link\": \"https://www.apple.com/macbook-air-m2/\"},\n",
    "    {\"id\": 5, \"name\": \"Dell Inspiron 15\", \"price\": 699, \"category\": \"laptop\", \"link\": \"https://www.dell.com/en-in/shop/dell-laptops/inspiron-15-laptop\"},\n",
    "]\n",
    "\n",
    "catalog_text = \"\\n\".join([\n",
    "    f\"ID: {p['id']}, Name: {p['name']}, Price: ${p['price']}, Category: {p['category']}, Link: {p['link']}\"\n",
    "    for p in products\n",
    "])\n",
    "\n",
    "\n",
    "# ----------------------------------\n",
    "# FALLBACK RECOMMENDATION (NO AI)\n",
    "# ----------------------------------\n",
    "def fallback_recommendation(user_input):\n",
    "    user_input_lower = user_input.lower()\n",
    "    fallback = []\n",
    "\n",
    "    price_match = re.findall(r'\\$?\\d+', user_input_lower)\n",
    "    max_price = int(price_match[0].replace('$', '')) if price_match else None\n",
    "\n",
    "    for p in products:\n",
    "        category_match = any(cat in user_input_lower for cat in [\"phone\", \"laptop\", \"tablet\"])\n",
    "        if category_match and p[\"category\"] in user_input_lower:\n",
    "            if max_price:\n",
    "                if p[\"price\"] <= max_price:\n",
    "                    fallback.append(p)\n",
    "            else:\n",
    "                fallback.append(p)\n",
    "    return fallback\n",
    "\n",
    "\n",
    "# ----------------------------------\n",
    "# MAIN FUNCTION (NO STREAMLIT)\n",
    "# ----------------------------------\n",
    "def get_recommendation(user_input):\n",
    "    if not user_input.strip():\n",
    "        return \"Please enter your product preference.\"\n",
    "\n",
    "    prompt = f\"\"\"\n",
    "You are a product recommendation AI.\n",
    "Here is the product list:\n",
    "{catalog_text}\n",
    "\n",
    "User preference: {user_input}\n",
    "\n",
    "Return ONLY the matching product IDs as a JSON array. Example: [1, 3]\n",
    "\"\"\"\n",
    "\n",
    "    try:\n",
    "        response = client.chat.completions.create(\n",
    "            model=\"gpt-3.5-turbo\",\n",
    "            messages=[\n",
    "                {\"role\": \"system\", \"content\": \"You are a helpful product recommendation engine.\"},\n",
    "                {\"role\": \"user\", \"content\": prompt}\n",
    "            ],\n",
    "            temperature=0.2,\n",
    "        )\n",
    "\n",
    "        ai_reply = response.choices[0].message[\"content\"].strip()\n",
    "\n",
    "        try:\n",
    "            recommended_ids = json.loads(ai_reply)\n",
    "            recommended_products = [p for p in products if p[\"id\"] in recommended_ids]\n",
    "\n",
    "            return recommended_products\n",
    "\n",
    "        except json.JSONDecodeError:\n",
    "            return f\"AI did not return valid JSON. Raw output:\\n{ai_reply}\"\n",
    "\n",
    "    except OpenAIError:\n",
    "        return fallback_recommendation(user_input)\n",
    "\n",
    "\n",
    "# ----------------------------------\n",
    "# COMMAND-LINE USE\n",
    "# ----------------------------------\n",
    "if __name__ == \"__main__\":\n",
    "    print(\"🛒 Product Recommendation System \")\n",
    "    user_input = input(\"Enter your preference (e.g., phone under $500): \")\n",
    "    result = get_recommendation(user_input)\n",
    "    print(\"\\nRecommendation Result:\")\n",
    "    print(result)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3a3b4dad-73b7-46b2-ac43-114181c2da8c",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

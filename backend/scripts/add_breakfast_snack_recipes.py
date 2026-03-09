#!/usr/bin/env python3
"""Add breakfast and snack recipes to improve meal type distribution."""

import json
from pathlib import Path

SEED_FILE = Path(__file__).parent.parent / "app" / "data" / "seed_recipes.json"


def make_recipe(
    name, description, ingredients, instructions, prep, cook, difficulty,
    servings, tags, score, nutrition
):
    return {
        "name": name,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "difficulty": difficulty,
        "servings": servings,
        "tags": tags,
        "autoimmune_score": score,
        "nutrition": nutrition,
        "source": "seeded",
    }


def ing(name, quantity, unit):
    return {"name": name, "quantity": quantity, "unit": unit}


def nutr(calories, protein, sodium, potassium, phosphorus):
    return {
        "calories": calories,
        "protein": protein,
        "sodium": sodium,
        "potassium": potassium,
        "phosphorus": phosphorus,
    }


def get_breakfast_recipes():
    recipes = []

    # 1. Mexican Breakfast Tacos
    recipes.append(make_recipe(
        "Mexican Breakfast Tacos with Black Beans",
        "Warm corn tortillas filled with seasoned black beans, scrambled eggs, avocado, and fresh cilantro.",
        [ing("eggs", 6, "whole"), ing("black beans", 1.0, "cup"),
         ing("corn tortillas", 8, "pieces"), ing("avocado", 1.0, "whole"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime juice", 1.0, "tbsp"),
         ing("cumin", 0.5, "tsp"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.25, "tsp")],
        ["Warm black beans in a small pot with cumin and a pinch of salt.",
         "Scramble eggs in olive oil over medium heat until just set.",
         "Warm corn tortillas on a dry skillet for 30 seconds each side.",
         "Fill tortillas with beans, scrambled eggs, and sliced avocado.",
         "Top with cilantro and a squeeze of lime."],
        10, 10, "beginner", 4,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(340, 18, 290, 480, 220)
    ))

    # 2. Avocado Toast with Lime and Cilantro
    recipes.append(make_recipe(
        "Avocado Toast with Lime and Cilantro",
        "Creamy mashed avocado on toasted gluten-free bread with fresh lime, cilantro, and a sprinkle of sea salt.",
        [ing("gluten-free bread", 4, "slices"), ing("avocado", 2.0, "whole"),
         ing("lime juice", 2.0, "tbsp"), ing("fresh cilantro", 2.0, "tbsp"),
         ing("sea salt", 0.25, "tsp"), ing("olive oil", 1.0, "tsp"),
         ing("red onion", 2.0, "tbsp")],
        ["Toast gluten-free bread slices until golden and crispy.",
         "Mash avocados with lime juice and sea salt.",
         "Spread mashed avocado generously on each toast.",
         "Top with finely diced red onion, cilantro, and a drizzle of olive oil."],
        5, 5, "beginner", 2,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        5, nutr(280, 6, 180, 490, 70)
    ))

    # 3. Tropical Fruit Smoothie Bowl
    recipes.append(make_recipe(
        "Tropical Fruit Smoothie Bowl",
        "A thick and creamy smoothie bowl made with mango, pineapple, and banana, topped with coconut and chia seeds.",
        [ing("frozen mango", 1.0, "cup"), ing("frozen pineapple", 0.5, "cup"),
         ing("banana", 1.0, "whole"), ing("coconut milk", 0.5, "cup"),
         ing("chia seeds", 1.0, "tbsp"), ing("shredded coconut", 2.0, "tbsp"),
         ing("granola", 0.25, "cup"), ing("honey", 1.0, "tsp")],
        ["Blend frozen mango, pineapple, banana, and coconut milk until thick and smooth.",
         "Pour into a bowl (mixture should be thicker than a regular smoothie).",
         "Top with chia seeds, shredded coconut, and granola.",
         "Drizzle with honey and serve immediately."],
        10, 0, "beginner", 2,
        ["breakfast", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly"],
        5, nutr(310, 5, 30, 420, 80)
    ))

    # 4. Chia Pudding with Mango
    recipes.append(make_recipe(
        "Chia Pudding with Mango and Coconut",
        "Overnight chia pudding made with coconut milk, topped with fresh mango and toasted coconut flakes.",
        [ing("chia seeds", 0.33, "cup"), ing("coconut milk", 1.5, "cups"),
         ing("honey", 1.0, "tbsp"), ing("vanilla extract", 0.5, "tsp"),
         ing("mango", 1.0, "whole"), ing("toasted coconut flakes", 2.0, "tbsp")],
        ["Stir chia seeds into coconut milk with honey and vanilla.",
         "Refrigerate for at least 4 hours or overnight, stirring once after 30 minutes.",
         "Dice fresh mango into small cubes.",
         "Serve chia pudding topped with mango and toasted coconut flakes."],
        10, 0, "beginner", 2,
        ["breakfast", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(260, 6, 25, 280, 110)
    ))

    # 5. Oatmeal with Cinnamon and Banana
    recipes.append(make_recipe(
        "Oatmeal with Cinnamon and Banana",
        "Warm and comforting oatmeal cooked with cinnamon, topped with sliced banana, walnuts, and a drizzle of honey.",
        [ing("rolled oats", 1.0, "cup"), ing("water", 2.0, "cups"),
         ing("banana", 1.0, "whole"), ing("cinnamon", 1.0, "tsp"),
         ing("walnuts", 2.0, "tbsp"), ing("honey", 1.0, "tbsp"),
         ing("salt", 0.125, "tsp")],
        ["Bring water to a boil, add oats and a pinch of salt.",
         "Reduce heat and simmer for 5 minutes, stirring occasionally.",
         "Stir in cinnamon during the last minute of cooking.",
         "Serve topped with sliced banana, chopped walnuts, and a drizzle of honey."],
        5, 8, "beginner", 2,
        ["breakfast", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        5, nutr(290, 8, 75, 380, 170)
    ))

    # 6. Sweet Potato Breakfast Hash
    recipes.append(make_recipe(
        "Sweet Potato Breakfast Hash",
        "Crispy diced sweet potatoes with onions, kale, and a fried egg on top.",
        [ing("sweet potato", 2.0, "whole"), ing("olive oil", 2.0, "tbsp"),
         ing("onion", 1.0, "whole"), ing("kale", 2.0, "cups"),
         ing("garlic cloves", 2.0, "whole"), ing("eggs", 4, "whole"),
         ing("cumin", 0.5, "tsp"), ing("salt", 0.25, "tsp"),
         ing("black pepper", 0.25, "tsp")],
        ["Dice sweet potatoes into small cubes and toss with olive oil and cumin.",
         "Cook sweet potatoes in a large skillet over medium-high heat for 12-15 minutes until crispy.",
         "Add diced onion and minced garlic, cook for 3 minutes.",
         "Add chopped kale and cook until wilted, about 2 minutes.",
         "Make 4 wells in the hash and crack an egg into each.",
         "Cover and cook until eggs are set, about 4 minutes. Season with salt and pepper."],
        15, 20, "beginner", 4,
        ["breakfast", "gluten-free", "dairy-free", "anti-inflammatory", "low-sodium"],
        5, nutr(280, 12, 190, 520, 150)
    ))

    # 7. Green Smoothie
    recipes.append(make_recipe(
        "Green Power Smoothie",
        "A nutrient-packed green smoothie with spinach, banana, avocado, and ginger.",
        [ing("spinach", 2.0, "cups"), ing("banana", 1.0, "whole"),
         ing("avocado", 0.5, "whole"), ing("fresh ginger", 0.5, "inch"),
         ing("coconut milk", 1.0, "cup"), ing("honey", 1.0, "tsp"),
         ing("ice", 0.5, "cup")],
        ["Add spinach, banana, avocado, and ginger to a blender.",
         "Pour in coconut milk and add ice.",
         "Blend on high until completely smooth, about 60 seconds.",
         "Taste and add honey if desired. Serve immediately."],
        5, 0, "beginner", 2,
        ["breakfast", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        5, nutr(220, 4, 60, 580, 70)
    ))

    # 8. Mexican Rice Porridge
    recipes.append(make_recipe(
        "Mexican Rice Porridge with Cinnamon",
        "A warm and comforting rice porridge made with coconut milk, cinnamon, and vanilla, inspired by traditional arroz con leche.",
        [ing("white rice", 0.5, "cup"), ing("coconut milk", 2.0, "cups"),
         ing("water", 1.0, "cup"), ing("cinnamon stick", 1.0, "whole"),
         ing("vanilla extract", 1.0, "tsp"), ing("honey", 2.0, "tbsp"),
         ing("ground cinnamon", 0.25, "tsp"), ing("raisins", 2.0, "tbsp")],
        ["Rinse rice and combine with water in a saucepan. Bring to a boil, then simmer until water is absorbed.",
         "Add coconut milk and cinnamon stick. Simmer on low for 20 minutes, stirring frequently.",
         "Stir in vanilla and honey. Remove cinnamon stick.",
         "Serve warm topped with raisins and a sprinkle of ground cinnamon."],
        5, 25, "beginner", 4,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(250, 4, 35, 180, 80)
    ))

    # 9. Coconut Yogurt Parfait
    recipes.append(make_recipe(
        "Coconut Yogurt Parfait with Berries",
        "Layers of creamy coconut yogurt, fresh mixed berries, and crunchy granola.",
        [ing("coconut yogurt", 2.0, "cups"), ing("blueberries", 0.5, "cup"),
         ing("strawberries", 0.5, "cup"), ing("granola", 0.5, "cup"),
         ing("honey", 1.0, "tbsp"), ing("chia seeds", 1.0, "tbsp")],
        ["Wash and slice strawberries. Rinse blueberries.",
         "Layer coconut yogurt, mixed berries, and granola in glasses or bowls.",
         "Repeat layers until glasses are full.",
         "Top with chia seeds and a drizzle of honey. Serve immediately."],
        10, 0, "beginner", 2,
        ["breakfast", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(270, 6, 40, 300, 90)
    ))

    # 10. Plantain Pancakes
    recipes.append(make_recipe(
        "Plantain Pancakes",
        "Naturally sweet and fluffy pancakes made from ripe plantains, eggs, and a touch of cinnamon.",
        [ing("ripe plantains", 2.0, "whole"), ing("eggs", 3, "whole"),
         ing("coconut oil", 2.0, "tbsp"), ing("cinnamon", 0.5, "tsp"),
         ing("baking powder", 0.5, "tsp"), ing("vanilla extract", 0.5, "tsp"),
         ing("salt", 0.125, "tsp")],
        ["Peel and slice plantains. Blend with eggs, cinnamon, baking powder, vanilla, and salt until smooth.",
         "Heat coconut oil in a skillet over medium heat.",
         "Pour 1/4 cup batter per pancake and cook for 2-3 minutes per side until golden.",
         "Serve warm with fresh fruit or a drizzle of honey."],
        10, 15, "beginner", 4,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(230, 8, 120, 350, 100)
    ))

    # 11. Breakfast Burrito Bowl
    recipes.append(make_recipe(
        "Breakfast Burrito Bowl",
        "All the flavors of a breakfast burrito in a bowl: seasoned rice, black beans, scrambled eggs, and fresh salsa verde.",
        [ing("rice", 1.0, "cup"), ing("black beans", 1.0, "cup"),
         ing("eggs", 6, "whole"), ing("avocado", 1.0, "whole"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime juice", 2.0, "tbsp"),
         ing("olive oil", 1.0, "tbsp"), ing("cumin", 0.5, "tsp"),
         ing("garlic powder", 0.25, "tsp"), ing("salt", 0.25, "tsp")],
        ["Cook rice according to package directions. Fluff with lime juice and chopped cilantro.",
         "Warm black beans with cumin and garlic powder.",
         "Scramble eggs in olive oil until just set.",
         "Assemble bowls: rice, beans, scrambled eggs, and sliced avocado.",
         "Top with extra cilantro and a squeeze of lime."],
        10, 20, "beginner", 4,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(380, 20, 310, 560, 240)
    ))

    # 12. Huevos a la Mexicana (Adapted)
    recipes.append(make_recipe(
        "Huevos a la Mexicana (Nightshade-Free)",
        "A nightshade-free take on the classic Mexican scrambled eggs, using zucchini and herbs instead of tomatoes and peppers.",
        [ing("eggs", 6, "whole"), ing("zucchini", 1.0, "whole"),
         ing("onion", 0.5, "whole"), ing("fresh cilantro", 0.25, "cup"),
         ing("olive oil", 1.0, "tbsp"), ing("cumin", 0.5, "tsp"),
         ing("garlic cloves", 2.0, "whole"), ing("salt", 0.25, "tsp"),
         ing("corn tortillas", 4, "pieces")],
        ["Dice zucchini and onion into small pieces. Mince garlic.",
         "Heat olive oil in a skillet over medium heat. Saute onion and garlic for 3 minutes.",
         "Add diced zucchini and cumin, cook for 4 minutes until softened.",
         "Pour in beaten eggs and scramble with the vegetables until just set.",
         "Serve with warm corn tortillas and fresh cilantro."],
        10, 10, "beginner", 4,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(220, 15, 180, 340, 180)
    ))

    # 13. Mediterranean Egg Cups
    recipes.append(make_recipe(
        "Mediterranean Egg Cups with Spinach",
        "Baked eggs in muffin tins with spinach, sun-dried tomatoes, and fresh herbs.",
        [ing("eggs", 8, "whole"), ing("spinach", 2.0, "cups"),
         ing("sun-dried tomatoes", 0.25, "cup"), ing("fresh basil", 2.0, "tbsp"),
         ing("olive oil", 1.0, "tbsp"), ing("garlic cloves", 2.0, "whole"),
         ing("dried oregano", 0.5, "tsp"), ing("salt", 0.25, "tsp")],
        ["Preheat oven to 375F. Grease a muffin tin with olive oil.",
         "Saute spinach and minced garlic until wilted. Chop sun-dried tomatoes.",
         "Divide spinach and sun-dried tomatoes among 8 muffin cups.",
         "Crack one egg into each cup. Season with oregano, salt, and basil.",
         "Bake for 12-15 minutes until eggs are set. Cool slightly before removing."],
        10, 15, "beginner", 4,
        ["mediterranean", "breakfast", "gluten-free", "dairy-free", "low-sodium"],
        3, nutr(160, 12, 200, 310, 170)
    ))

    # 14. Shakshuka Breakfast Bowl
    recipes.append(make_recipe(
        "Shakshuka Breakfast Bowl",
        "Eggs poached in a warm spiced tomato and red pepper sauce, served with crusty bread for dipping.",
        [ing("eggs", 4, "whole"), ing("crushed tomatoes", 2.0, "cups"),
         ing("red bell pepper", 1.0, "whole"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("cumin", 1.0, "tsp"),
         ing("smoked paprika", 0.5, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("salt", 0.25, "tsp")],
        ["Heat olive oil in a deep skillet. Saute diced onion and red bell pepper for 5 minutes.",
         "Add minced garlic, cumin, and smoked paprika. Cook for 1 minute.",
         "Pour in crushed tomatoes and simmer for 10 minutes until thickened.",
         "Make 4 wells in the sauce and crack an egg into each.",
         "Cover and cook for 5-7 minutes until egg whites are set but yolks are still runny.",
         "Garnish with fresh cilantro and serve."],
        10, 20, "intermediate", 4,
        ["mediterranean", "breakfast", "gluten-free", "dairy-free", "vegetarian"],
        2, nutr(230, 12, 350, 520, 170)
    ))

    # 15. Za'atar Avocado Toast
    recipes.append(make_recipe(
        "Za'atar Avocado Toast",
        "Creamy avocado on gluten-free toast, seasoned with fragrant za'atar spice blend and a squeeze of lemon.",
        [ing("gluten-free bread", 4, "slices"), ing("avocado", 2.0, "whole"),
         ing("za'atar spice blend", 2.0, "tsp"), ing("lemon juice", 1.0, "tbsp"),
         ing("olive oil", 2.0, "tsp"), ing("sea salt", 0.25, "tsp"),
         ing("cherry tomatoes", 0.5, "cup")],
        ["Toast gluten-free bread until golden and crispy.",
         "Mash avocados with lemon juice and sea salt.",
         "Spread mashed avocado on each toast slice.",
         "Halve cherry tomatoes and arrange on top.",
         "Sprinkle generously with za'atar and drizzle with olive oil."],
        5, 5, "beginner", 2,
        ["mediterranean", "breakfast", "gluten-free", "dairy-free", "vegetarian"],
        3, nutr(290, 6, 190, 510, 75)
    ))

    return recipes


def get_snack_recipes():
    recipes = []

    # 1. Guacamole
    recipes.append(make_recipe(
        "Classic Guacamole",
        "Creamy and fresh guacamole with ripe avocados, lime, cilantro, and onion.",
        [ing("avocado", 3.0, "whole"), ing("lime juice", 2.0, "tbsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("red onion", 0.25, "cup"),
         ing("garlic cloves", 1.0, "whole"), ing("salt", 0.25, "tsp"),
         ing("cumin", 0.25, "tsp")],
        ["Halve avocados and remove pits. Scoop into a bowl.",
         "Mash with a fork to desired consistency (chunky or smooth).",
         "Stir in lime juice, minced garlic, and cumin.",
         "Fold in diced red onion and chopped cilantro. Season with salt.",
         "Serve immediately with vegetable sticks or plantain chips."],
        10, 0, "beginner", 4,
        ["mexican", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(160, 2, 100, 490, 50)
    ))

    # 2. Pico de Gallo
    recipes.append(make_recipe(
        "Fresh Pico de Gallo",
        "A classic Mexican fresh salsa with diced tomatoes, onion, jalapeno, cilantro, and lime.",
        [ing("roma tomatoes", 4.0, "whole"), ing("white onion", 0.5, "whole"),
         ing("jalapeno", 1.0, "whole"), ing("fresh cilantro", 0.33, "cup"),
         ing("lime juice", 2.0, "tbsp"), ing("salt", 0.25, "tsp")],
        ["Dice tomatoes and place in a bowl, draining excess liquid.",
         "Finely dice white onion and jalapeno (remove seeds for less heat).",
         "Chop cilantro and add to the bowl.",
         "Toss with lime juice and salt. Let sit for 15 minutes before serving."],
        15, 0, "beginner", 6,
        ["mexican", "snack", "gluten-free", "dairy-free", "vegetarian", "low-sodium"],
        2, nutr(50, 1, 100, 230, 25)
    ))

    # 3. Hummus
    recipes.append(make_recipe(
        "Classic Hummus",
        "Smooth and creamy hummus made with chickpeas, tahini, lemon, and garlic.",
        [ing("chickpeas", 2.0, "cups"), ing("tahini", 0.25, "cup"),
         ing("lemon juice", 3.0, "tbsp"), ing("garlic cloves", 2.0, "whole"),
         ing("olive oil", 3.0, "tbsp"), ing("cumin", 0.5, "tsp"),
         ing("salt", 0.25, "tsp"), ing("water", 3.0, "tbsp")],
        ["Drain and rinse chickpeas. Reserve a few for garnish.",
         "Blend tahini and lemon juice in a food processor for 1 minute until smooth.",
         "Add chickpeas, garlic, cumin, and salt. Blend for 2 minutes.",
         "With processor running, drizzle in olive oil and water until very smooth.",
         "Serve drizzled with olive oil and reserved chickpeas."],
        10, 0, "beginner", 6,
        ["mediterranean", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        4, nutr(180, 7, 150, 200, 130)
    ))

    # 4. Baba Ganoush
    recipes.append(make_recipe(
        "Smoky Baba Ganoush",
        "A smoky roasted eggplant dip blended with tahini, lemon, and garlic.",
        [ing("eggplant", 2.0, "whole"), ing("tahini", 2.0, "tbsp"),
         ing("lemon juice", 2.0, "tbsp"), ing("garlic cloves", 2.0, "whole"),
         ing("olive oil", 2.0, "tbsp"), ing("salt", 0.25, "tsp"),
         ing("smoked paprika", 0.25, "tsp"), ing("fresh parsley", 1.0, "tbsp")],
        ["Roast whole eggplants directly over a gas flame or under a broiler until charred and collapsed, about 15 minutes.",
         "Let cool, then scoop out the soft flesh, discarding skin.",
         "Blend eggplant flesh with tahini, lemon juice, garlic, and salt until smooth.",
         "Drizzle with olive oil and sprinkle with smoked paprika and parsley."],
        10, 20, "intermediate", 6,
        ["mediterranean", "snack", "gluten-free", "dairy-free", "vegetarian", "low-sodium"],
        3, nutr(90, 2, 110, 270, 40)
    ))

    # 5. Roasted Chickpeas
    recipes.append(make_recipe(
        "Crispy Roasted Chickpeas",
        "Crunchy oven-roasted chickpeas seasoned with cumin, garlic, and a hint of smoked paprika.",
        [ing("chickpeas", 2.0, "cups"), ing("olive oil", 2.0, "tbsp"),
         ing("cumin", 1.0, "tsp"), ing("garlic powder", 0.5, "tsp"),
         ing("smoked paprika", 0.5, "tsp"), ing("salt", 0.25, "tsp")],
        ["Preheat oven to 400F. Drain, rinse, and thoroughly dry chickpeas with paper towels.",
         "Toss chickpeas with olive oil, cumin, garlic powder, paprika, and salt.",
         "Spread in a single layer on a baking sheet.",
         "Roast for 30-35 minutes, shaking pan halfway, until very crispy.",
         "Let cool completely on the pan for maximum crunch."],
        5, 35, "beginner", 4,
        ["mediterranean", "snack", "gluten-free", "dairy-free", "vegetarian", "low-sodium"],
        3, nutr(170, 7, 180, 210, 130)
    ))

    # 6. Trail Mix
    recipes.append(make_recipe(
        "Autoimmune-Friendly Trail Mix",
        "A nourishing trail mix with walnuts, almonds, coconut flakes, dried cranberries, and pumpkin seeds.",
        [ing("walnuts", 0.5, "cup"), ing("almonds", 0.5, "cup"),
         ing("pumpkin seeds", 0.25, "cup"), ing("dried cranberries", 0.33, "cup"),
         ing("coconut flakes", 0.25, "cup"), ing("dark chocolate chips", 0.25, "cup")],
        ["Combine all ingredients in a large bowl and toss to mix evenly.",
         "Portion into small bags or containers for grab-and-go snacking.",
         "Store in an airtight container for up to 2 weeks."],
        5, 0, "beginner", 6,
        ["snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        5, nutr(210, 6, 10, 200, 130)
    ))

    # 7. Plantain Chips
    recipes.append(make_recipe(
        "Baked Plantain Chips",
        "Thin and crispy baked plantain chips seasoned with sea salt and lime.",
        [ing("green plantains", 3.0, "whole"), ing("olive oil", 2.0, "tbsp"),
         ing("sea salt", 0.5, "tsp"), ing("lime juice", 1.0, "tbsp")],
        ["Preheat oven to 375F. Peel plantains and slice very thinly (1/16 inch) using a mandoline.",
         "Toss slices with olive oil and arrange in a single layer on baking sheets.",
         "Bake for 15-18 minutes, flipping halfway, until golden and crispy.",
         "Immediately season with sea salt and a squeeze of lime. Cool on rack."],
        15, 18, "beginner", 4,
        ["mexican", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(140, 1, 130, 350, 25)
    ))

    # 8. Jicama with Lime and Chili
    recipes.append(make_recipe(
        "Jicama Sticks with Lime and Tajin",
        "Crunchy jicama sticks sprinkled with lime juice, a chili-lime seasoning, and a pinch of salt.",
        [ing("jicama", 1.0, "whole"), ing("lime juice", 2.0, "tbsp"),
         ing("chili-lime seasoning", 1.0, "tsp"), ing("salt", 0.125, "tsp")],
        ["Peel jicama and cut into thin sticks about 3 inches long.",
         "Arrange on a plate and squeeze lime juice over all the sticks.",
         "Sprinkle with chili-lime seasoning and a pinch of salt.",
         "Serve immediately as a refreshing, crunchy snack."],
        10, 0, "beginner", 4,
        ["mexican", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(60, 1, 80, 200, 20)
    ))

    # 9. Cucumber Tzatziki
    recipes.append(make_recipe(
        "Cucumber Tzatziki with Coconut Yogurt",
        "A dairy-free version of classic Greek tzatziki using coconut yogurt, cucumber, dill, and lemon.",
        [ing("coconut yogurt", 1.5, "cups"), ing("cucumber", 1.0, "whole"),
         ing("fresh dill", 2.0, "tbsp"), ing("lemon juice", 1.0, "tbsp"),
         ing("garlic cloves", 1.0, "whole"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.25, "tsp")],
        ["Grate cucumber and squeeze out excess moisture using a clean kitchen towel.",
         "Combine coconut yogurt, grated cucumber, minced garlic, and lemon juice.",
         "Stir in chopped fresh dill and olive oil.",
         "Season with salt and refrigerate for 30 minutes before serving."],
        15, 0, "beginner", 6,
        ["mediterranean", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(70, 1, 120, 150, 30)
    ))

    # 10. Stuffed Dates
    recipes.append(make_recipe(
        "Stuffed Dates with Almond Butter",
        "Medjool dates stuffed with creamy almond butter and topped with a sprinkle of sea salt.",
        [ing("medjool dates", 12, "whole"), ing("almond butter", 3.0, "tbsp"),
         ing("sea salt", 0.125, "tsp"), ing("dark chocolate chips", 2.0, "tbsp")],
        ["Slice each date lengthwise and remove the pit.",
         "Fill each date with about 1 teaspoon of almond butter.",
         "Optionally, press a few chocolate chips into the almond butter.",
         "Sprinkle with a tiny pinch of sea salt. Refrigerate until serving."],
        10, 0, "beginner", 6,
        ["snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        5, nutr(120, 2, 30, 180, 40)
    ))

    # 11. Energy Bites
    recipes.append(make_recipe(
        "No-Bake Energy Bites",
        "Quick and easy energy bites made with oats, almond butter, honey, and dark chocolate chips.",
        [ing("rolled oats", 1.0, "cup"), ing("almond butter", 0.5, "cup"),
         ing("honey", 0.33, "cup"), ing("dark chocolate chips", 0.25, "cup"),
         ing("chia seeds", 1.0, "tbsp"), ing("coconut flakes", 2.0, "tbsp"),
         ing("vanilla extract", 0.5, "tsp")],
        ["Combine oats, almond butter, honey, and vanilla in a bowl and stir until well mixed.",
         "Fold in chocolate chips, chia seeds, and coconut flakes.",
         "Refrigerate for 30 minutes to firm up.",
         "Roll into 1-inch balls. Store in the refrigerator for up to 1 week."],
        10, 0, "beginner", 12,
        ["snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        5, nutr(110, 3, 15, 120, 60)
    ))

    # 12. Roasted Sweet Potato Wedges
    recipes.append(make_recipe(
        "Roasted Sweet Potato Wedges",
        "Crispy on the outside, tender on the inside sweet potato wedges with herbs and olive oil.",
        [ing("sweet potatoes", 3.0, "whole"), ing("olive oil", 2.0, "tbsp"),
         ing("garlic powder", 0.5, "tsp"), ing("dried rosemary", 0.5, "tsp"),
         ing("smoked paprika", 0.25, "tsp"), ing("salt", 0.25, "tsp")],
        ["Preheat oven to 425F. Cut sweet potatoes into wedge shapes.",
         "Toss wedges with olive oil, garlic powder, rosemary, paprika, and salt.",
         "Spread in a single layer on a baking sheet, cut side down.",
         "Roast for 25-30 minutes, flipping halfway, until crispy and golden."],
        10, 30, "beginner", 4,
        ["snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "low-sodium"],
        4, nutr(150, 2, 170, 440, 55)
    ))

    # 13. Mexican Street Corn Cups
    recipes.append(make_recipe(
        "Mexican Street Corn Cups (Esquites)",
        "Warm corn kernels tossed with lime, cilantro, chili-lime seasoning, and a dairy-free crema.",
        [ing("corn kernels", 3.0, "cups"), ing("olive oil", 1.0, "tbsp"),
         ing("lime juice", 2.0, "tbsp"), ing("fresh cilantro", 0.25, "cup"),
         ing("chili-lime seasoning", 1.0, "tsp"), ing("coconut yogurt", 0.25, "cup"),
         ing("garlic powder", 0.25, "tsp"), ing("salt", 0.25, "tsp")],
        ["Heat olive oil in a skillet over medium-high heat. Add corn and cook for 5-7 minutes until slightly charred.",
         "Remove from heat and toss with lime juice, chili-lime seasoning, and garlic powder.",
         "Stir in coconut yogurt to make a creamy coating.",
         "Serve in cups topped with fresh cilantro and an extra squeeze of lime."],
        10, 10, "beginner", 4,
        ["mexican", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        4, nutr(130, 4, 170, 280, 80)
    ))

    # 14. Olive Tapenade
    recipes.append(make_recipe(
        "Mediterranean Olive Tapenade",
        "A savory spread of kalamata olives, capers, lemon, and fresh herbs, perfect with vegetables or crackers.",
        [ing("kalamata olives", 1.0, "cup"), ing("capers", 1.0, "tbsp"),
         ing("lemon juice", 1.0, "tbsp"), ing("garlic cloves", 1.0, "whole"),
         ing("olive oil", 2.0, "tbsp"), ing("fresh parsley", 2.0, "tbsp"),
         ing("dried oregano", 0.5, "tsp")],
        ["Drain olives and capers. Pat dry with paper towels.",
         "Pulse olives, capers, garlic, and lemon juice in a food processor until coarsely chopped.",
         "Drizzle in olive oil and pulse a few more times until desired texture.",
         "Stir in chopped parsley and oregano. Serve with vegetable sticks or gluten-free crackers."],
        10, 0, "beginner", 6,
        ["mediterranean", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly"],
        4, nutr(80, 1, 280, 40, 10)
    ))

    # 15. Fruit and Nut Plate
    recipes.append(make_recipe(
        "Mediterranean Fruit and Nut Plate",
        "An elegant assortment of fresh and dried fruits, nuts, and a drizzle of honey for a satisfying snack.",
        [ing("almonds", 0.25, "cup"), ing("walnuts", 0.25, "cup"),
         ing("dried apricots", 0.25, "cup"), ing("fresh figs", 4, "whole"),
         ing("grapes", 1.0, "cup"), ing("honey", 1.0, "tbsp")],
        ["Arrange almonds and walnuts in small clusters on a serving plate.",
         "Halve fresh figs and arrange alongside the nuts.",
         "Add clusters of grapes and dried apricots around the plate.",
         "Drizzle honey lightly over the fruit. Serve as a shared snack or appetizer."],
        10, 0, "beginner", 4,
        ["mediterranean", "snack", "gluten-free", "dairy-free", "vegetarian", "anti-inflammatory", "kidney-friendly", "low-sodium"],
        5, nutr(190, 5, 15, 320, 90)
    ))

    return recipes


def main():
    with open(SEED_FILE) as f:
        recipes = json.load(f)

    existing_names = {r["name"] for r in recipes}

    # Count current meal types
    meal_counts = {"breakfast": 0, "lunch": 0, "dinner": 0, "snack": 0}
    for r in recipes:
        tags = [t.lower() for t in r.get("tags", [])]
        for m in meal_counts:
            if m in tags:
                meal_counts[m] += 1
                break
        else:
            meal_counts["dinner"] += 1

    print(f"Current: {len(recipes)} recipes")
    for m, c in meal_counts.items():
        print(f"  {m}: {c} ({c/len(recipes)*100:.1f}%)")

    new_breakfast = get_breakfast_recipes()
    new_snacks = get_snack_recipes()

    added_breakfast = 0
    added_snack = 0
    skipped = []

    for r in new_breakfast:
        if r["name"] in existing_names:
            skipped.append(r["name"])
            continue
        recipes.append(r)
        existing_names.add(r["name"])
        added_breakfast += 1

    for r in new_snacks:
        if r["name"] in existing_names:
            skipped.append(r["name"])
            continue
        recipes.append(r)
        existing_names.add(r["name"])
        added_snack += 1

    print(f"\nAdded {added_breakfast} breakfast recipes, {added_snack} snack recipes")
    if skipped:
        print(f"Skipped (duplicate names): {skipped}")

    # Final counts
    total = len(recipes)
    final_meals = {"breakfast": 0, "lunch": 0, "dinner": 0, "snack": 0}
    for r in recipes:
        tags = [t.lower() for t in r.get("tags", [])]
        for m in final_meals:
            if m in tags:
                final_meals[m] += 1
                break
        else:
            final_meals["dinner"] += 1

    print(f"\nFinal: {total} recipes")
    for m, c in final_meals.items():
        print(f"  {m}: {c} ({c/total*100:.1f}%)")

    with open(SEED_FILE, "w") as f:
        json.dump(recipes, f, indent=2)
    print(f"\nWrote {total} recipes to {SEED_FILE}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Add manual Mexican and Mediterranean recipes to reach cuisine distribution targets."""

import json
import os
from collections import Counter
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


def get_mexican_recipes():
    recipes = []

    # 1. Grilled Fish Tacos
    recipes.append(make_recipe(
        "Grilled Fish Tacos with Cabbage Slaw",
        "Light and flavorful grilled white fish tacos topped with a tangy cabbage slaw and fresh lime.",
        [ing("tilapia fillets", 1.0, "lb"), ing("corn tortillas", 8, "pieces"),
         ing("green cabbage", 2.0, "cups"), ing("fresh cilantro", 0.25, "cup"),
         ing("lime juice", 2.0, "tbsp"), ing("avocado", 1.0, "whole"),
         ing("olive oil", 1.0, "tbsp"), ing("cumin", 1.0, "tsp"),
         ing("garlic powder", 0.5, "tsp"), ing("salt", 0.25, "tsp")],
        ["Season tilapia with cumin, garlic powder, salt, and a drizzle of olive oil.",
         "Grill fish over medium-high heat for 3-4 minutes per side until cooked through.",
         "Toss shredded cabbage with lime juice and chopped cilantro.",
         "Warm corn tortillas on the grill for 30 seconds each side.",
         "Flake fish into tortillas, top with cabbage slaw and sliced avocado."],
        15, 10, "beginner", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free", "anti-inflammatory", "kidney-friendly"],
        4, nutr(320, 28, 280, 520, 250)
    ))

    # 2. Shrimp Ceviche
    recipes.append(make_recipe(
        "Shrimp Ceviche",
        "Fresh shrimp marinated in citrus juice with cucumber, red onion, and cilantro.",
        [ing("cooked shrimp", 1.0, "lb"), ing("lime juice", 0.5, "cup"),
         ing("lemon juice", 0.25, "cup"), ing("cucumber", 1.0, "whole"),
         ing("red onion", 0.5, "whole"), ing("fresh cilantro", 0.33, "cup"),
         ing("avocado", 1.0, "whole"), ing("jalapeño", 1.0, "whole"),
         ing("salt", 0.5, "tsp"), ing("olive oil", 1.0, "tbsp")],
        ["Dice cooked shrimp into bite-sized pieces and place in a bowl.",
         "Pour lime and lemon juice over shrimp, toss to coat, and refrigerate for 20 minutes.",
         "Dice cucumber, red onion, and jalapeño. Chop cilantro.",
         "Combine shrimp with vegetables, drizzle with olive oil, and season with salt.",
         "Serve topped with diced avocado."],
        30, 0, "beginner", 4,
        ["mexican", "lunch", "gluten-free", "dairy-free", "anti-inflammatory", "low-sodium"],
        4, nutr(210, 24, 320, 400, 220)
    ))

    # 3. Salmon Tostadas
    recipes.append(make_recipe(
        "Salmon Tostadas with Avocado Crema",
        "Crispy corn tostadas topped with seasoned baked salmon and a creamy avocado sauce.",
        [ing("salmon fillets", 1.0, "lb"), ing("corn tostada shells", 8, "pieces"),
         ing("avocado", 2.0, "whole"), ing("lime juice", 3.0, "tbsp"),
         ing("shredded cabbage", 2.0, "cups"), ing("fresh cilantro", 0.25, "cup"),
         ing("cumin", 1.0, "tsp"), ing("garlic powder", 0.5, "tsp"),
         ing("salt", 0.25, "tsp"), ing("olive oil", 1.0, "tbsp")],
        ["Season salmon with cumin, garlic powder, salt, and olive oil. Bake at 400°F for 12-15 minutes.",
         "Blend avocado with lime juice and a pinch of salt to make crema.",
         "Flake the baked salmon into large pieces.",
         "Layer tostada shells with shredded cabbage, salmon, and avocado crema.",
         "Garnish with cilantro and a squeeze of lime."],
        15, 15, "beginner", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(380, 30, 310, 580, 290)
    ))

    # 4. Chicken Tortilla Soup (No Tomato)
    recipes.append(make_recipe(
        "Chicken Tortilla Soup (Nightshade-Free)",
        "A warming chicken soup with corn tortilla strips, avocado, and lime, made without tomatoes for autoimmune friendliness.",
        [ing("chicken breast", 1.5, "lb"), ing("chicken broth", 6.0, "cups"),
         ing("corn tortillas", 4, "pieces"), ing("avocado", 1.0, "whole"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("cumin", 1.5, "tsp"), ing("dried oregano", 1.0, "tsp"),
         ing("lime juice", 2.0, "tbsp"), ing("olive oil", 2.0, "tbsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("salt", 0.5, "tsp")],
        ["Sauté diced onion and minced garlic in olive oil until softened.",
         "Add chicken broth, cumin, oregano, and salt. Bring to a boil.",
         "Add chicken breasts, reduce heat, and simmer for 20 minutes until cooked through.",
         "Remove chicken, shred with two forks, and return to pot.",
         "Cut tortillas into strips and bake at 375°F for 8 minutes until crispy.",
         "Serve soup topped with tortilla strips, diced avocado, cilantro, and lime juice."],
        15, 30, "intermediate", 6,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free", "anti-inflammatory", "kidney-friendly"],
        5, nutr(310, 32, 480, 450, 240)
    ))

    # 5. Pozole Verde
    recipes.append(make_recipe(
        "Pozole Verde with Chicken",
        "Traditional Mexican hominy soup in a tangy green tomatillo broth with shredded chicken.",
        [ing("chicken thighs", 1.5, "lb"), ing("hominy", 2.0, "cups"),
         ing("tomatillos", 6.0, "whole"), ing("poblano pepper", 1.0, "whole"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("chicken broth", 4.0, "cups"), ing("fresh cilantro", 0.5, "cup"),
         ing("dried oregano", 1.0, "tsp"), ing("shredded cabbage", 1.0, "cup"),
         ing("radishes", 4.0, "whole"), ing("lime", 2.0, "whole"),
         ing("salt", 0.5, "tsp")],
        ["Simmer chicken thighs in broth with half the onion and garlic for 25 minutes. Shred chicken.",
         "Roast tomatillos and poblano under the broiler until charred, about 8 minutes.",
         "Blend roasted tomatillos, poblano, remaining onion, garlic, and cilantro until smooth.",
         "Add green sauce and hominy to the broth, simmer for 15 minutes.",
         "Return shredded chicken to pot and season with oregano and salt.",
         "Serve topped with shredded cabbage, sliced radishes, and lime wedges."],
        20, 45, "intermediate", 6,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free"],
        3, nutr(350, 30, 520, 480, 270)
    ))

    # 6. Caldo de Pollo
    recipes.append(make_recipe(
        "Caldo de Pollo",
        "Classic Mexican chicken soup with vegetables, a nourishing comfort food staple.",
        [ing("chicken drumsticks", 2.0, "lb"), ing("carrots", 3.0, "whole"),
         ing("zucchini", 2.0, "whole"), ing("chayote", 1.0, "whole"),
         ing("corn on the cob", 2.0, "ears"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 4.0, "whole"), ing("fresh cilantro", 0.5, "cup"),
         ing("lime", 2.0, "whole"), ing("salt", 1.0, "tsp"), ing("water", 10.0, "cups")],
        ["Place chicken, quartered onion, and whole garlic in a large pot. Cover with water and bring to a boil.",
         "Skim any foam, reduce heat, and simmer for 30 minutes.",
         "Cut carrots, zucchini, chayote, and corn into large chunks. Add to pot.",
         "Simmer another 20 minutes until vegetables are tender.",
         "Season with salt and serve with fresh cilantro and lime wedges."],
        15, 50, "beginner", 6,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free", "anti-inflammatory", "low-sodium", "kidney-friendly"],
        5, nutr(280, 26, 350, 520, 210)
    ))

    # 7. Black Bean Burrito Bowl
    recipes.append(make_recipe(
        "Black Bean Burrito Bowl",
        "A hearty bowl with seasoned black beans, rice, avocado, and fresh toppings.",
        [ing("black beans", 1.5, "cups"), ing("brown rice", 1.0, "cup"),
         ing("avocado", 1.0, "whole"), ing("corn kernels", 0.5, "cup"),
         ing("red onion", 0.5, "whole"), ing("lime juice", 2.0, "tbsp"),
         ing("cumin", 1.0, "tsp"), ing("garlic powder", 0.5, "tsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.25, "tsp"), ing("romaine lettuce", 2.0, "cups")],
        ["Cook brown rice according to package directions.",
         "Heat black beans with cumin, garlic powder, and salt in a saucepan.",
         "Dice red onion and avocado. Mix corn with lime juice and cilantro.",
         "Assemble bowls: rice, beans, lettuce, corn salsa, avocado, and onion.",
         "Drizzle with olive oil and extra lime juice."],
        10, 25, "beginner", 4,
        ["mexican", "lunch", "dinner", "gluten-free", "dairy-free", "vegan", "kidney-friendly"],
        4, nutr(420, 16, 280, 650, 200)
    ))

    # 8. Bean and Rice Casserole
    recipes.append(make_recipe(
        "Mexican Bean and Rice Casserole",
        "A comforting baked casserole with layers of seasoned beans, rice, and green chiles.",
        [ing("pinto beans", 2.0, "cups"), ing("white rice", 1.5, "cups"),
         ing("green chiles", 4.0, "oz"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 2.0, "whole"), ing("cumin", 1.5, "tsp"),
         ing("dried oregano", 1.0, "tsp"), ing("vegetable broth", 1.5, "cups"),
         ing("olive oil", 2.0, "tbsp"), ing("salt", 0.5, "tsp"),
         ing("fresh cilantro", 0.25, "cup")],
        ["Cook rice and set aside. Sauté diced onion and garlic in olive oil.",
         "Add beans, green chiles, cumin, oregano, and broth to the pan. Simmer 10 minutes.",
         "Layer rice and bean mixture in a baking dish.",
         "Bake at 375°F for 20 minutes until bubbly.",
         "Garnish with fresh cilantro before serving."],
        15, 35, "beginner", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free", "vegan"],
        4, nutr(380, 14, 420, 500, 190)
    ))

    # 9. Carne Asada Salad
    recipes.append(make_recipe(
        "Carne Asada Salad",
        "Grilled marinated steak sliced over a bed of crisp greens with avocado and lime dressing.",
        [ing("flank steak", 1.0, "lb"), ing("romaine lettuce", 6.0, "cups"),
         ing("avocado", 1.0, "whole"), ing("cucumber", 1.0, "whole"),
         ing("radishes", 4.0, "whole"), ing("red onion", 0.5, "whole"),
         ing("lime juice", 3.0, "tbsp"), ing("olive oil", 2.0, "tbsp"),
         ing("cumin", 1.0, "tsp"), ing("garlic powder", 0.5, "tsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("salt", 0.5, "tsp")],
        ["Marinate steak with lime juice, olive oil, cumin, garlic powder, and salt for at least 30 minutes.",
         "Grill steak over high heat for 4-5 minutes per side for medium. Let rest 5 minutes.",
         "Chop romaine, dice cucumber and radishes, slice red onion.",
         "Slice steak thinly against the grain.",
         "Arrange salad, top with steak and sliced avocado, drizzle with extra lime and olive oil."],
        40, 10, "intermediate", 4,
        ["mexican", "dinner", "lunch", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(380, 32, 350, 620, 260)
    ))

    # 10. Grilled Chicken Fajitas (Adapted)
    recipes.append(make_recipe(
        "Grilled Chicken Fajitas (Nightshade-Free)",
        "Sizzling grilled chicken with onions and squash, served in warm tortillas without bell peppers.",
        [ing("chicken breast", 1.5, "lb"), ing("zucchini", 2.0, "whole"),
         ing("onion", 2.0, "whole"), ing("corn tortillas", 8, "pieces"),
         ing("lime juice", 3.0, "tbsp"), ing("olive oil", 2.0, "tbsp"),
         ing("cumin", 1.5, "tsp"), ing("dried oregano", 1.0, "tsp"),
         ing("garlic powder", 1.0, "tsp"), ing("salt", 0.5, "tsp"),
         ing("avocado", 1.0, "whole"), ing("fresh cilantro", 0.25, "cup")],
        ["Slice chicken into strips and marinate with lime juice, olive oil, cumin, oregano, garlic powder, and salt.",
         "Slice zucchini and onions into strips.",
         "Grill chicken strips over high heat for 5-6 minutes per side.",
         "Grill vegetables alongside until charred and tender, about 8 minutes.",
         "Warm tortillas on the grill and serve with chicken, veggies, avocado, and cilantro."],
        20, 15, "beginner", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free", "anti-inflammatory", "kidney-friendly"],
        5, nutr(360, 35, 320, 550, 270)
    ))

    # 11. Carnitas Lettuce Wraps
    recipes.append(make_recipe(
        "Carnitas Lettuce Wraps",
        "Tender slow-cooked pork carnitas served in crisp butter lettuce cups with pickled onion.",
        [ing("pork shoulder", 2.0, "lb"), ing("butter lettuce", 1.0, "head"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 4.0, "whole"),
         ing("orange juice", 0.5, "cup"), ing("lime juice", 2.0, "tbsp"),
         ing("cumin", 2.0, "tsp"), ing("dried oregano", 1.0, "tsp"),
         ing("salt", 1.0, "tsp"), ing("red onion", 1.0, "whole"),
         ing("apple cider vinegar", 0.25, "cup"), ing("fresh cilantro", 0.25, "cup")],
        ["Season pork with cumin, oregano, and salt. Place in slow cooker with onion, garlic, and orange juice.",
         "Cook on low for 8 hours or high for 4 hours until falling apart.",
         "Quick-pickle red onion slices in vinegar with a pinch of salt for 30 minutes.",
         "Shred pork and crisp under the broiler for 5 minutes.",
         "Serve in lettuce cups topped with pickled onion, cilantro, and lime."],
        15, 240, "intermediate", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free", "low-sodium"],
        4, nutr(340, 30, 380, 450, 240)
    ))

    # 12. Enchiladas Verdes
    recipes.append(make_recipe(
        "Enchiladas Verdes (Tomatillo Sauce)",
        "Corn tortillas filled with shredded chicken and bathed in a tangy tomatillo green sauce.",
        [ing("chicken breast", 1.5, "lb"), ing("corn tortillas", 12, "pieces"),
         ing("tomatillos", 1.0, "lb"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 2.0, "whole"), ing("jalapeño", 1.0, "whole"),
         ing("fresh cilantro", 0.5, "cup"), ing("chicken broth", 0.5, "cup"),
         ing("olive oil", 2.0, "tbsp"), ing("salt", 0.5, "tsp"),
         ing("avocado", 1.0, "whole")],
        ["Poach chicken breast in water until cooked, about 20 minutes. Shred.",
         "Roast tomatillos, onion half, garlic, and jalapeño under broiler until charred.",
         "Blend roasted vegetables with cilantro, broth, and salt until smooth.",
         "Dip tortillas in warm sauce, fill with chicken, and roll. Place seam-down in baking dish.",
         "Pour remaining sauce over enchiladas and bake at 375°F for 15 minutes.",
         "Serve topped with sliced avocado."],
        25, 40, "intermediate", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(350, 30, 450, 480, 260)
    ))

    # 13. Chile Verde with Pork
    recipes.append(make_recipe(
        "Chile Verde with Pork",
        "Tender braised pork in a bright, tangy green chile sauce with tomatillos.",
        [ing("pork shoulder", 2.0, "lb"), ing("tomatillos", 1.0, "lb"),
         ing("poblano peppers", 2.0, "whole"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 4.0, "whole"), ing("chicken broth", 1.0, "cup"),
         ing("fresh cilantro", 0.5, "cup"), ing("cumin", 1.0, "tsp"),
         ing("dried oregano", 0.5, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.75, "tsp"), ing("lime juice", 1.0, "tbsp")],
        ["Cut pork into 1-inch cubes. Brown in olive oil in a Dutch oven, then remove.",
         "Roast tomatillos and poblanos under the broiler until blistered.",
         "Blend roasted vegetables with onion, garlic, cilantro, and broth.",
         "Return pork to pot, pour green sauce over, add cumin and oregano.",
         "Simmer covered for 1.5 hours until pork is very tender.",
         "Stir in lime juice and adjust salt before serving."],
        20, 100, "intermediate", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(380, 34, 450, 520, 270)
    ))

    # 14. Chilaquiles Verdes
    recipes.append(make_recipe(
        "Chilaquiles Verdes",
        "Crispy tortilla chips simmered in green tomatillo salsa, topped with eggs and avocado.",
        [ing("corn tortillas", 8, "pieces"), ing("tomatillos", 0.75, "lb"),
         ing("onion", 0.5, "whole"), ing("garlic cloves", 2.0, "whole"),
         ing("jalapeño", 1.0, "whole"), ing("fresh cilantro", 0.25, "cup"),
         ing("eggs", 4.0, "whole"), ing("avocado", 1.0, "whole"),
         ing("olive oil", 3.0, "tbsp"), ing("salt", 0.5, "tsp"),
         ing("crumbled queso fresco", 0.25, "cup")],
        ["Cut tortillas into triangles and fry in oil until crispy. Drain on paper towels.",
         "Roast tomatillos, onion, garlic, and jalapeño. Blend with cilantro and salt.",
         "Simmer salsa in a skillet, add tortilla chips, and toss to coat.",
         "Fry eggs sunny-side up in a separate pan.",
         "Serve chilaquiles topped with fried eggs, avocado slices, and crumbled queso."],
        15, 20, "intermediate", 4,
        ["mexican", "breakfast", "gluten-free"],
        3, nutr(420, 18, 380, 480, 230)
    ))

    # 15. Huevos Rancheros (Adapted)
    recipes.append(make_recipe(
        "Huevos Rancheros (Nightshade-Free)",
        "Fried eggs on corn tortillas with a roasted tomatillo-avocado sauce instead of traditional tomato salsa.",
        [ing("eggs", 4.0, "whole"), ing("corn tortillas", 4, "pieces"),
         ing("tomatillos", 0.5, "lb"), ing("avocado", 1.0, "whole"),
         ing("black beans", 1.0, "cup"), ing("fresh cilantro", 0.25, "cup"),
         ing("lime juice", 1.0, "tbsp"), ing("onion", 0.25, "whole"),
         ing("garlic clove", 1.0, "whole"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.25, "tsp")],
        ["Roast tomatillos, onion, and garlic under the broiler. Blend with avocado, cilantro, lime, and salt.",
         "Warm black beans in a small saucepan with a splash of water.",
         "Warm tortillas in a dry skillet until pliable.",
         "Fry eggs in olive oil to desired doneness.",
         "Place tortillas on plates, spread with beans, top with eggs, and spoon sauce over."],
        15, 15, "beginner", 2,
        ["mexican", "breakfast", "gluten-free"],
        4, nutr(440, 22, 350, 580, 250)
    ))

    # 16. Mexican Breakfast Scramble
    recipes.append(make_recipe(
        "Mexican Breakfast Scramble",
        "Fluffy scrambled eggs with zucchini, onion, and fresh herbs, served with warm tortillas.",
        [ing("eggs", 6.0, "whole"), ing("zucchini", 1.0, "whole"),
         ing("onion", 0.5, "whole"), ing("fresh cilantro", 0.25, "cup"),
         ing("corn tortillas", 4, "pieces"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.25, "tsp"), ing("cumin", 0.5, "tsp"),
         ing("avocado", 1.0, "whole")],
        ["Dice zucchini and onion. Sauté in olive oil until softened, about 5 minutes.",
         "Beat eggs with cumin and salt. Pour over vegetables.",
         "Scramble gently over medium-low heat until just set.",
         "Serve with warm tortillas, sliced avocado, and cilantro."],
        10, 10, "beginner", 3,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "kidney-friendly"],
        4, nutr(320, 20, 280, 420, 220)
    ))

    # 17. Guacamole Bowl
    recipes.append(make_recipe(
        "Guacamole Power Bowl",
        "A satisfying bowl built around fresh guacamole with rice, beans, and grilled chicken.",
        [ing("chicken breast", 1.0, "lb"), ing("avocado", 2.0, "whole"),
         ing("lime juice", 3.0, "tbsp"), ing("brown rice", 1.0, "cup"),
         ing("black beans", 1.0, "cup"), ing("red onion", 0.5, "whole"),
         ing("fresh cilantro", 0.33, "cup"), ing("cumin", 1.0, "tsp"),
         ing("salt", 0.5, "tsp"), ing("olive oil", 1.0, "tbsp")],
        ["Season chicken with cumin and salt, grill for 6 minutes per side. Slice.",
         "Cook brown rice according to package directions.",
         "Mash avocados with lime juice, diced onion, cilantro, and salt.",
         "Warm black beans in a saucepan.",
         "Assemble bowls with rice, beans, chicken, and a generous scoop of guacamole."],
        15, 25, "beginner", 4,
        ["mexican", "lunch", "dinner", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(480, 34, 380, 700, 300)
    ))

    # 18. Elote-Inspired Salad
    recipes.append(make_recipe(
        "Elote-Inspired Corn Salad",
        "A deconstructed Mexican street corn salad with charred corn, lime, and a creamy avocado dressing.",
        [ing("corn kernels", 3.0, "cups"), ing("avocado", 1.0, "whole"),
         ing("lime juice", 2.0, "tbsp"), ing("red onion", 0.25, "whole"),
         ing("fresh cilantro", 0.25, "cup"), ing("olive oil", 2.0, "tbsp"),
         ing("cumin", 0.5, "tsp"), ing("chili powder", 0.5, "tsp"),
         ing("salt", 0.25, "tsp"), ing("romaine lettuce", 4.0, "cups")],
        ["Char corn in a hot skillet with olive oil until blackened in spots, about 8 minutes.",
         "Blend half the avocado with lime juice and a splash of water for the dressing.",
         "Toss charred corn with diced onion, cilantro, cumin, and chili powder.",
         "Arrange romaine on plates and top with corn mixture.",
         "Drizzle with avocado dressing and top with remaining diced avocado."],
        10, 10, "beginner", 4,
        ["mexican", "lunch", "side", "gluten-free", "dairy-free", "vegan"],
        4, nutr(250, 6, 180, 450, 130)
    ))

    # 19. Mexican Street Corn Soup
    recipes.append(make_recipe(
        "Mexican Street Corn Soup",
        "Creamy roasted corn soup inspired by elote flavors, with lime and fresh herbs.",
        [ing("corn kernels", 4.0, "cups"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("vegetable broth", 4.0, "cups"),
         ing("coconut milk", 0.5, "cup"), ing("lime juice", 2.0, "tbsp"),
         ing("cumin", 1.0, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("salt", 0.5, "tsp")],
        ["Roast corn, diced onion, and garlic in olive oil over high heat until charred.",
         "Transfer to a pot, add broth, cumin, and salt. Simmer for 15 minutes.",
         "Blend half the soup until smooth, return to pot for a chunky-creamy texture.",
         "Stir in coconut milk and lime juice.",
         "Serve garnished with cilantro."],
        10, 25, "beginner", 4,
        ["mexican", "lunch", "soup", "gluten-free", "dairy-free", "vegan", "anti-inflammatory"],
        4, nutr(240, 6, 380, 420, 140)
    ))

    # 20. Chicken Mole (Simplified)
    recipes.append(make_recipe(
        "Simplified Chicken Mole",
        "A rich and complex mole sauce with dark chocolate and warm spices over tender chicken.",
        [ing("chicken thighs", 2.0, "lb"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 4.0, "whole"), ing("ancho chile", 3.0, "whole"),
         ing("dark chocolate", 1.0, "oz"), ing("sesame seeds", 2.0, "tbsp"),
         ing("cumin", 1.0, "tsp"), ing("cinnamon stick", 1.0, "whole"),
         ing("chicken broth", 2.0, "cups"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.75, "tsp"), ing("corn tortillas", 8, "pieces")],
        ["Toast ancho chiles in a dry skillet, then soak in hot water for 15 minutes.",
         "Sauté diced onion and garlic in olive oil until golden.",
         "Blend soaked chiles, onion, garlic, sesame seeds, cumin, broth, and chocolate until smooth.",
         "Brown chicken thighs in the pot, pour mole sauce over.",
         "Simmer covered for 35 minutes until chicken is very tender.",
         "Serve with warm corn tortillas."],
        25, 50, "intermediate", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(420, 34, 480, 520, 290)
    ))

    # 21. Birria-Style Beef Stew
    recipes.append(make_recipe(
        "Birria-Style Beef Stew",
        "A deeply flavorful slow-braised beef stew with warm dried chiles and aromatic spices.",
        [ing("beef chuck", 2.5, "lb"), ing("guajillo chiles", 4.0, "whole"),
         ing("ancho chiles", 2.0, "whole"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 5.0, "whole"), ing("cumin", 1.5, "tsp"),
         ing("dried oregano", 1.0, "tsp"), ing("cloves", 3.0, "whole"),
         ing("apple cider vinegar", 2.0, "tbsp"), ing("beef broth", 3.0, "cups"),
         ing("bay leaves", 2.0, "whole"), ing("salt", 1.0, "tsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime", 2.0, "whole")],
        ["Toast dried chiles in a dry pan, soak in hot water for 15 minutes.",
         "Blend chiles with onion, garlic, cumin, oregano, cloves, vinegar, and a cup of broth.",
         "Cut beef into large chunks, season with salt, and brown in a heavy pot.",
         "Pour chile sauce over beef, add remaining broth and bay leaves.",
         "Braise covered at 325°F for 3 hours until beef is fall-apart tender.",
         "Serve with fresh cilantro and lime wedges."],
        30, 195, "advanced", 8,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(380, 38, 520, 480, 280)
    ))

    # 22. Albondigas Soup
    recipes.append(make_recipe(
        "Albondigas Soup",
        "Comforting Mexican meatball soup with herbs and vegetables in a light broth.",
        [ing("ground turkey", 1.0, "lb"), ing("white rice", 0.25, "cup"),
         ing("egg", 1.0, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("cumin", 1.0, "tsp"), ing("carrots", 2.0, "whole"),
         ing("zucchini", 2.0, "whole"), ing("onion", 1.0, "whole"),
         ing("chicken broth", 8.0, "cups"), ing("fresh cilantro", 0.33, "cup"),
         ing("lime", 2.0, "whole"), ing("salt", 0.75, "tsp"),
         ing("dried oregano", 0.5, "tsp")],
        ["Mix ground turkey with cooked rice, egg, minced garlic, cumin, half the cilantro, and salt. Form into 1-inch balls.",
         "Bring broth to a simmer with diced onion and oregano.",
         "Gently add meatballs to simmering broth. Cook 10 minutes.",
         "Add diced carrots and zucchini. Simmer another 15 minutes.",
         "Serve topped with cilantro and lime wedges."],
        20, 30, "intermediate", 6,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free", "kidney-friendly"],
        4, nutr(280, 24, 450, 440, 230)
    ))

    # 23. Nopales Salad
    recipes.append(make_recipe(
        "Nopales Salad",
        "A refreshing salad made with tender cactus paddles, tomato, onion, and fresh herbs.",
        [ing("nopales", 2.0, "cups"), ing("roma tomatoes", 2.0, "whole"),
         ing("white onion", 0.5, "whole"), ing("fresh cilantro", 0.33, "cup"),
         ing("jalapeño", 1.0, "whole"), ing("lime juice", 2.0, "tbsp"),
         ing("olive oil", 2.0, "tbsp"), ing("dried oregano", 0.5, "tsp"),
         ing("salt", 0.25, "tsp"), ing("avocado", 1.0, "whole")],
        ["Clean nopales by trimming spines and edges. Cut into strips.",
         "Boil nopales in salted water for 10 minutes until tender. Drain and rinse to remove slime.",
         "Dice tomatoes, onion, and jalapeño. Chop cilantro.",
         "Toss nopales with vegetables, lime juice, olive oil, oregano, and salt.",
         "Top with sliced avocado and serve at room temperature."],
        15, 12, "beginner", 4,
        ["mexican", "lunch", "side", "gluten-free", "dairy-free", "vegan", "low-sodium", "kidney-friendly"],
        4, nutr(160, 4, 180, 400, 80)
    ))

    # 24. Chayote and Chicken Stew
    recipes.append(make_recipe(
        "Chayote and Chicken Stew",
        "A light and nourishing Mexican stew with tender chayote squash and chicken in herbed broth.",
        [ing("chicken thighs", 1.5, "lb"), ing("chayote", 2.0, "whole"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("carrots", 2.0, "whole"), ing("chicken broth", 5.0, "cups"),
         ing("cumin", 1.0, "tsp"), ing("dried oregano", 0.5, "tsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime juice", 1.0, "tbsp"),
         ing("olive oil", 1.0, "tbsp"), ing("salt", 0.5, "tsp")],
        ["Brown chicken thighs in olive oil. Remove and set aside.",
         "Sauté diced onion and garlic in the same pot until softened.",
         "Add broth, cumin, oregano, and salt. Return chicken and bring to a simmer.",
         "Peel and cube chayote and carrots. Add to pot and simmer 25 minutes.",
         "Shred chicken, return to pot, stir in lime juice and cilantro."],
        15, 40, "intermediate", 6,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free", "anti-inflammatory", "kidney-friendly"],
        5, nutr(290, 28, 400, 480, 230)
    ))

    # 25. Calabacitas
    recipes.append(make_recipe(
        "Calabacitas (Mexican Squash Sauté)",
        "A simple and traditional side dish of sautéed zucchini with corn and onion.",
        [ing("zucchini", 3.0, "whole"), ing("corn kernels", 1.0, "cup"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 2.0, "whole"),
         ing("olive oil", 2.0, "tbsp"), ing("cumin", 0.5, "tsp"),
         ing("salt", 0.25, "tsp"), ing("fresh cilantro", 0.25, "cup"),
         ing("lime juice", 1.0, "tbsp")],
        ["Dice zucchini into half-inch cubes. Dice onion and mince garlic.",
         "Sauté onion and garlic in olive oil until fragrant, about 3 minutes.",
         "Add zucchini and corn. Cook over medium heat for 8-10 minutes until tender.",
         "Season with cumin and salt, finish with lime juice and cilantro."],
        10, 12, "beginner", 4,
        ["mexican", "side", "dinner", "gluten-free", "dairy-free", "vegan", "low-sodium", "kidney-friendly", "anti-inflammatory"],
        5, nutr(130, 4, 120, 380, 90)
    ))

    # 26. Arroz con Pollo
    recipes.append(make_recipe(
        "Arroz con Pollo",
        "Classic Mexican chicken and rice cooked together in a savory herbed broth.",
        [ing("chicken thighs", 2.0, "lb"), ing("long grain rice", 1.5, "cups"),
         ing("chicken broth", 2.5, "cups"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("carrots", 2.0, "whole"),
         ing("frozen peas", 0.5, "cup"), ing("cumin", 1.5, "tsp"),
         ing("dried oregano", 1.0, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("salt", 0.75, "tsp")],
        ["Brown chicken thighs in olive oil, then remove and set aside.",
         "Sauté diced onion, garlic, and diced carrots in the same pot.",
         "Add rice and toast for 2 minutes, stirring constantly.",
         "Pour in broth, cumin, oregano, and salt. Nestle chicken on top.",
         "Cover and cook on low heat for 25 minutes until rice is fluffy and chicken is cooked.",
         "Stir in peas, cover for 5 minutes, garnish with cilantro."],
        15, 35, "intermediate", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        4, nutr(440, 32, 480, 500, 280)
    ))

    # 27. Mexican Rice and Beans
    recipes.append(make_recipe(
        "Mexican Rice and Beans",
        "Fluffy seasoned rice with tender pinto beans, a staple side that works as a complete meal.",
        [ing("long grain rice", 1.5, "cups"), ing("pinto beans", 1.5, "cups"),
         ing("vegetable broth", 2.5, "cups"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 2.0, "whole"), ing("cumin", 1.5, "tsp"),
         ing("dried oregano", 0.5, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("fresh cilantro", 0.25, "cup"),
         ing("lime juice", 1.0, "tbsp")],
        ["Sauté diced onion and garlic in olive oil until softened.",
         "Add rice and toast for 2 minutes. Add cumin and oregano.",
         "Pour in broth and salt. Bring to a boil, cover, reduce heat, simmer 18 minutes.",
         "Warm pinto beans in a separate pan.",
         "Fluff rice, fold in beans, finish with lime juice and cilantro."],
        10, 25, "beginner", 6,
        ["mexican", "side", "dinner", "gluten-free", "dairy-free", "vegan", "kidney-friendly"],
        4, nutr(350, 12, 320, 480, 180)
    ))

    # 28. Sopes with Chicken
    recipes.append(make_recipe(
        "Chicken Sopes",
        "Thick corn masa bases topped with refried beans, shredded chicken, and fresh garnishes.",
        [ing("masa harina", 2.0, "cups"), ing("water", 1.25, "cups"),
         ing("chicken breast", 1.0, "lb"), ing("refried beans", 1.0, "cup"),
         ing("avocado", 1.0, "whole"), ing("shredded cabbage", 1.0, "cup"),
         ing("lime juice", 2.0, "tbsp"), ing("olive oil", 2.0, "tbsp"),
         ing("cumin", 1.0, "tsp"), ing("salt", 0.5, "tsp"),
         ing("fresh cilantro", 0.25, "cup")],
        ["Mix masa harina with warm water and salt to form dough. Divide into 8 balls, flatten into thick discs.",
         "Cook masa discs on a hot griddle for 3 minutes each side. Pinch up edges to form a rim.",
         "Season chicken with cumin and grill until cooked. Shred.",
         "Spread refried beans on each sope, top with shredded chicken.",
         "Garnish with cabbage, avocado, cilantro, and lime juice."],
        25, 20, "intermediate", 4,
        ["mexican", "dinner", "lunch", "gluten-free", "dairy-free"],
        4, nutr(400, 28, 420, 520, 250)
    ))

    # 29. Tamales with Chicken and Green Chile
    recipes.append(make_recipe(
        "Chicken and Green Chile Tamales",
        "Traditional steamed masa tamales filled with seasoned chicken and roasted green chiles.",
        [ing("masa harina", 3.0, "cups"), ing("chicken broth", 1.5, "cups"),
         ing("olive oil", 0.5, "cup"), ing("chicken breast", 1.0, "lb"),
         ing("green chiles", 4.0, "oz"), ing("dried corn husks", 20, "pieces"),
         ing("cumin", 1.0, "tsp"), ing("garlic powder", 0.5, "tsp"),
         ing("salt", 1.0, "tsp"), ing("baking powder", 1.0, "tsp")],
        ["Soak corn husks in hot water for 30 minutes. Poach and shred chicken.",
         "Mix masa harina with broth, olive oil, salt, and baking powder until a soft dough forms.",
         "Mix shredded chicken with green chiles, cumin, and garlic powder.",
         "Spread masa on corn husks, add a spoonful of filling, fold and tie.",
         "Steam tamales upright in a steamer pot for 45 minutes until masa pulls away from husk."],
        45, 50, "advanced", 10,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(300, 18, 420, 300, 180)
    ))

    # 30. Dairy-Free Quesadillas
    recipes.append(make_recipe(
        "Dairy-Free Chicken Quesadillas",
        "Crispy corn tortilla quesadillas filled with seasoned chicken and dairy-free cheese.",
        [ing("corn tortillas", 8, "pieces"), ing("chicken breast", 1.0, "lb"),
         ing("dairy-free cheese shreds", 1.0, "cup"), ing("onion", 0.5, "whole"),
         ing("zucchini", 1.0, "whole"), ing("cumin", 1.0, "tsp"),
         ing("garlic powder", 0.5, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.25, "tsp"), ing("avocado", 1.0, "whole"),
         ing("lime juice", 1.0, "tbsp")],
        ["Season chicken with cumin, garlic powder, and salt. Grill and shred.",
         "Sauté diced zucchini and onion in olive oil until tender.",
         "Place tortillas on a griddle, add chicken, vegetables, and dairy-free cheese to one half.",
         "Fold and cook until crispy on both sides and cheese melts.",
         "Serve with sliced avocado and lime wedges."],
        15, 15, "beginner", 4,
        ["mexican", "lunch", "dinner", "gluten-free", "dairy-free"],
        4, nutr(380, 30, 350, 440, 240)
    ))

    # 31. Chicken Flautas
    recipes.append(make_recipe(
        "Baked Chicken Flautas",
        "Crispy rolled corn tortillas filled with seasoned shredded chicken, baked instead of fried.",
        [ing("corn tortillas", 12, "pieces"), ing("chicken breast", 1.5, "lb"),
         ing("onion", 0.5, "whole"), ing("garlic cloves", 2.0, "whole"),
         ing("cumin", 1.0, "tsp"), ing("dried oregano", 0.5, "tsp"),
         ing("chicken broth", 0.25, "cup"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("avocado", 1.0, "whole"),
         ing("shredded cabbage", 1.0, "cup"), ing("lime juice", 1.0, "tbsp")],
        ["Poach chicken, shred, and mix with sautéed onion, garlic, cumin, oregano, broth, and salt.",
         "Warm tortillas briefly to make them pliable.",
         "Place filling in each tortilla and roll tightly. Place seam-down on a baking sheet.",
         "Brush with olive oil and bake at 425°F for 18-20 minutes until golden and crispy.",
         "Serve with shredded cabbage, avocado slices, and lime."],
        20, 25, "intermediate", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        4, nutr(340, 30, 400, 420, 250)
    ))

    # 32. Churro-Spiced Sweet Potato Bites
    recipes.append(make_recipe(
        "Churro-Spiced Sweet Potato Bites",
        "Roasted sweet potato cubes tossed with cinnamon-sugar churro seasoning, a healthy snack.",
        [ing("sweet potatoes", 2.0, "lb"), ing("coconut oil", 2.0, "tbsp"),
         ing("cinnamon", 1.5, "tsp"), ing("coconut sugar", 2.0, "tbsp"),
         ing("vanilla extract", 1.0, "tsp"), ing("salt", 0.25, "tsp")],
        ["Peel sweet potatoes and cut into 1-inch cubes.",
         "Toss with melted coconut oil, cinnamon, coconut sugar, vanilla, and salt.",
         "Spread on a baking sheet in a single layer.",
         "Roast at 400°F for 25-30 minutes, flipping halfway, until caramelized and tender."],
        10, 30, "beginner", 6,
        ["mexican", "snack", "gluten-free", "dairy-free", "vegan", "anti-inflammatory"],
        4, nutr(180, 3, 120, 450, 70)
    ))

    # 33. Mexican Fruit Salad
    recipes.append(make_recipe(
        "Mexican Fruit Salad with Chile-Lime Dressing",
        "A vibrant mix of tropical fruits with a tangy chile-lime dressing, a refreshing side or snack.",
        [ing("mango", 2.0, "whole"), ing("pineapple", 2.0, "cups"),
         ing("watermelon", 2.0, "cups"), ing("cucumber", 1.0, "whole"),
         ing("jicama", 1.0, "cup"), ing("lime juice", 3.0, "tbsp"),
         ing("chili powder", 0.5, "tsp"), ing("salt", 0.25, "tsp"),
         ing("fresh mint", 2.0, "tbsp")],
        ["Dice mango, pineapple, watermelon, cucumber, and jicama into bite-sized pieces.",
         "Combine all fruit in a large bowl.",
         "Whisk lime juice, chili powder, and salt together.",
         "Drizzle dressing over fruit and toss gently. Garnish with mint."],
        15, 0, "beginner", 6,
        ["mexican", "snack", "side", "gluten-free", "dairy-free", "vegan", "low-sodium", "kidney-friendly", "anti-inflammatory"],
        5, nutr(120, 2, 80, 340, 40)
    ))

    # 34. Breakfast Tacos
    recipes.append(make_recipe(
        "Breakfast Tacos with Eggs and Avocado",
        "Simple corn tortilla tacos filled with scrambled eggs, avocado, and a squeeze of lime.",
        [ing("eggs", 6.0, "whole"), ing("corn tortillas", 6, "pieces"),
         ing("avocado", 1.0, "whole"), ing("onion", 0.25, "whole"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime juice", 1.0, "tbsp"),
         ing("olive oil", 1.0, "tbsp"), ing("salt", 0.25, "tsp"),
         ing("cumin", 0.5, "tsp")],
        ["Scramble eggs with cumin and salt in olive oil. Add diced onion halfway through.",
         "Warm corn tortillas on a dry griddle.",
         "Fill tortillas with scrambled eggs and sliced avocado.",
         "Top with cilantro and a squeeze of lime."],
        5, 8, "beginner", 3,
        ["mexican", "breakfast", "gluten-free", "dairy-free", "kidney-friendly"],
        4, nutr(350, 18, 260, 420, 210)
    ))

    # 35. Sopa de Fideo
    recipes.append(make_recipe(
        "Sopa de Fideo",
        "A light and comforting Mexican noodle soup with toasted vermicelli in a savory broth.",
        [ing("fideo noodles", 7.0, "oz"), ing("chicken broth", 6.0, "cups"),
         ing("tomatillos", 4.0, "whole"), ing("onion", 0.5, "whole"),
         ing("garlic cloves", 2.0, "whole"), ing("olive oil", 2.0, "tbsp"),
         ing("cumin", 0.5, "tsp"), ing("salt", 0.5, "tsp"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime", 1.0, "whole")],
        ["Toast fideo noodles in olive oil until golden brown, stirring constantly.",
         "Blend tomatillos, onion, and garlic until smooth.",
         "Add blended sauce to the pot with noodles and cook for 2 minutes.",
         "Pour in chicken broth, cumin, and salt. Simmer for 10 minutes until noodles are tender.",
         "Serve with cilantro and lime wedges."],
        5, 15, "beginner", 4,
        ["mexican", "lunch", "soup", "dairy-free"],
        4, nutr(220, 8, 480, 280, 110)
    ))

    # 36. Black Bean Soup
    recipes.append(make_recipe(
        "Mexican Black Bean Soup",
        "A hearty and smoky black bean soup with cumin and topped with avocado and lime.",
        [ing("dried black beans", 1.0, "lb"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 4.0, "whole"), ing("cumin", 2.0, "tsp"),
         ing("dried oregano", 1.0, "tsp"), ing("vegetable broth", 6.0, "cups"),
         ing("olive oil", 2.0, "tbsp"), ing("salt", 0.75, "tsp"),
         ing("avocado", 1.0, "whole"), ing("lime juice", 2.0, "tbsp"),
         ing("fresh cilantro", 0.25, "cup")],
        ["Soak beans overnight, drain and rinse.",
         "Sauté diced onion and garlic in olive oil until softened.",
         "Add beans, broth, cumin, oregano, and salt. Bring to a boil.",
         "Reduce heat and simmer for 1.5 hours until beans are very tender.",
         "Blend half the soup for a creamy-chunky texture.",
         "Serve topped with avocado, cilantro, and lime juice."],
        15, 100, "beginner", 6,
        ["mexican", "lunch", "dinner", "soup", "gluten-free", "dairy-free", "vegan", "anti-inflammatory"],
        4, nutr(290, 16, 350, 620, 180)
    ))

    # 37. Sopa de Lima
    recipes.append(make_recipe(
        "Sopa de Lima (Yucatan Lime Soup)",
        "A fragrant Yucatecan soup with shredded chicken, fried tortilla strips, and lots of lime.",
        [ing("chicken breast", 1.0, "lb"), ing("chicken broth", 6.0, "cups"),
         ing("limes", 4.0, "whole"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("corn tortillas", 4, "pieces"),
         ing("dried oregano", 1.0, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("fresh cilantro", 0.25, "cup"),
         ing("avocado", 1.0, "whole")],
        ["Simmer chicken in broth with half the onion and garlic for 20 minutes. Shred chicken.",
         "Sauté remaining diced onion and garlic in olive oil until fragrant.",
         "Add broth back, along with oregano and the juice of 3 limes.",
         "Cut tortillas into strips and bake at 400°F until crispy.",
         "Return shredded chicken to soup and simmer 5 minutes.",
         "Serve with tortilla strips, avocado, cilantro, and remaining lime wedges."],
        15, 30, "intermediate", 4,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(300, 28, 420, 440, 230)
    ))

    # 38. Mexican Omelette
    recipes.append(make_recipe(
        "Mexican Omelette",
        "A fluffy omelette filled with black beans, avocado, and fresh cilantro.",
        [ing("eggs", 3.0, "whole"), ing("black beans", 0.25, "cup"),
         ing("avocado", 0.5, "whole"), ing("onion", 0.25, "whole"),
         ing("fresh cilantro", 2.0, "tbsp"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.125, "tsp"), ing("cumin", 0.25, "tsp"),
         ing("lime juice", 1.0, "tsp")],
        ["Beat eggs with salt and cumin.",
         "Heat olive oil in a nonstick pan over medium heat.",
         "Pour in eggs and cook until edges set. Lift edges to let uncooked egg flow under.",
         "When almost set, add black beans and diced onion to one half.",
         "Fold omelette, slide onto plate, top with avocado, cilantro, and lime."],
        5, 5, "beginner", 1,
        ["mexican", "breakfast", "gluten-free", "kidney-friendly"],
        4, nutr(380, 20, 300, 480, 230)
    ))

    # 39. Molletes
    recipes.append(make_recipe(
        "Molletes",
        "Open-faced Mexican bean and cheese toasts, adapted with dairy-free cheese for autoimmune friendliness.",
        [ing("bolillo rolls", 4, "pieces"), ing("refried beans", 1.5, "cups"),
         ing("dairy-free cheese shreds", 1.0, "cup"), ing("avocado", 1.0, "whole"),
         ing("pico de gallo", 0.5, "cup"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.125, "tsp")],
        ["Slice bolillo rolls in half lengthwise and toast lightly under the broiler.",
         "Spread a generous layer of refried beans on each half.",
         "Top with dairy-free cheese shreds.",
         "Broil for 3-4 minutes until cheese melts and beans are bubbly.",
         "Serve topped with diced avocado and pico de gallo."],
        10, 8, "beginner", 4,
        ["mexican", "breakfast", "lunch", "dairy-free"],
        3, nutr(360, 14, 480, 400, 170)
    ))

    # 40. Grilled Steak Tacos
    recipes.append(make_recipe(
        "Grilled Steak Tacos",
        "Tender grilled skirt steak in warm corn tortillas with fresh onion, cilantro, and lime.",
        [ing("skirt steak", 1.0, "lb"), ing("corn tortillas", 8, "pieces"),
         ing("white onion", 0.5, "whole"), ing("fresh cilantro", 0.33, "cup"),
         ing("lime", 2.0, "whole"), ing("olive oil", 1.0, "tbsp"),
         ing("cumin", 1.0, "tsp"), ing("garlic powder", 0.5, "tsp"),
         ing("salt", 0.5, "tsp")],
        ["Season steak with cumin, garlic powder, salt, and olive oil. Rest 15 minutes.",
         "Grill over high heat for 3-4 minutes per side for medium.",
         "Let steak rest 5 minutes, then slice thinly against the grain.",
         "Warm tortillas on the grill.",
         "Serve steak in tortillas with diced onion, cilantro, and lime wedges."],
        20, 10, "beginner", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        4, nutr(360, 30, 380, 440, 250)
    ))

    # 41. Chicken Tinga
    recipes.append(make_recipe(
        "Chicken Tinga",
        "Shredded chicken braised in a smoky chipotle-tomatillo sauce, served over rice or in tacos.",
        [ing("chicken breast", 1.5, "lb"), ing("tomatillos", 0.5, "lb"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("chipotle in adobo", 2.0, "tbsp"), ing("chicken broth", 0.5, "cup"),
         ing("dried oregano", 1.0, "tsp"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("corn tortillas", 8, "pieces")],
        ["Poach chicken in water for 20 minutes, then shred.",
         "Roast tomatillos under the broiler. Blend with chipotle, garlic, and broth.",
         "Sauté sliced onion in olive oil until caramelized.",
         "Add shredded chicken and sauce to the onions. Simmer 15 minutes.",
         "Serve in warm tortillas or over rice."],
        15, 40, "intermediate", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(320, 32, 450, 460, 250)
    ))

    # 42. Shrimp Tacos with Mango Salsa
    recipes.append(make_recipe(
        "Shrimp Tacos with Mango Salsa",
        "Seasoned grilled shrimp tacos topped with a bright mango and cilantro salsa.",
        [ing("large shrimp", 1.0, "lb"), ing("corn tortillas", 8, "pieces"),
         ing("mango", 1.0, "whole"), ing("red onion", 0.25, "whole"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime juice", 2.0, "tbsp"),
         ing("olive oil", 1.0, "tbsp"), ing("cumin", 1.0, "tsp"),
         ing("garlic powder", 0.5, "tsp"), ing("salt", 0.25, "tsp"),
         ing("shredded cabbage", 1.0, "cup")],
        ["Peel and devein shrimp. Toss with cumin, garlic powder, salt, and olive oil.",
         "Dice mango and red onion. Mix with cilantro and lime juice for salsa.",
         "Grill shrimp for 2-3 minutes per side until pink and curled.",
         "Warm tortillas on the grill.",
         "Assemble tacos with shredded cabbage, shrimp, and mango salsa."],
        20, 8, "beginner", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free", "anti-inflammatory", "low-sodium"],
        4, nutr(290, 26, 300, 420, 230)
    ))

    # 43. Pork Tamales with Red Chile
    recipes.append(make_recipe(
        "Pork Tamales with Red Chile Sauce",
        "Traditional pork-filled tamales in a rich ancho and guajillo chile sauce.",
        [ing("pork shoulder", 1.5, "lb"), ing("masa harina", 3.0, "cups"),
         ing("ancho chiles", 3.0, "whole"), ing("guajillo chiles", 3.0, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("cumin", 1.0, "tsp"),
         ing("dried oregano", 0.5, "tsp"), ing("olive oil", 0.5, "cup"),
         ing("pork broth", 1.5, "cups"), ing("dried corn husks", 20, "pieces"),
         ing("salt", 1.0, "tsp"), ing("baking powder", 1.0, "tsp")],
        ["Braise pork shoulder in water with garlic and salt until tender, about 2 hours. Shred.",
         "Toast and soak dried chiles. Blend with garlic, cumin, oregano, and broth for sauce.",
         "Mix masa harina with broth, olive oil, baking powder, and salt until fluffy.",
         "Soak corn husks. Spread masa on husks, add pork and a spoonful of chile sauce.",
         "Fold husks and steam for 45 minutes until masa firms up."],
        40, 165, "advanced", 10,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(320, 20, 450, 320, 200)
    ))

    # 44. Taco Salad Bowl
    recipes.append(make_recipe(
        "Mexican Taco Salad Bowl",
        "A crunchy and fresh salad bowl with seasoned ground turkey, beans, and creamy avocado dressing.",
        [ing("ground turkey", 1.0, "lb"), ing("romaine lettuce", 6.0, "cups"),
         ing("black beans", 1.0, "cup"), ing("corn kernels", 0.5, "cup"),
         ing("avocado", 1.0, "whole"), ing("lime juice", 2.0, "tbsp"),
         ing("cumin", 1.5, "tsp"), ing("garlic powder", 0.5, "tsp"),
         ing("onion powder", 0.5, "tsp"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("fresh cilantro", 0.25, "cup")],
        ["Brown ground turkey with cumin, garlic powder, onion powder, and salt.",
         "Blend half the avocado with lime juice and water for a creamy dressing.",
         "Chop romaine and divide among bowls.",
         "Top with seasoned turkey, black beans, corn, and diced avocado.",
         "Drizzle with avocado dressing and garnish with cilantro."],
        10, 12, "beginner", 4,
        ["mexican", "lunch", "dinner", "gluten-free", "dairy-free"],
        4, nutr(380, 30, 420, 600, 270)
    ))

    # 45. Chicken Pozole Rojo
    recipes.append(make_recipe(
        "Chicken Pozole Rojo",
        "A vibrant red pozole with chicken, hominy, and a rich dried chile broth.",
        [ing("chicken thighs", 1.5, "lb"), ing("hominy", 2.0, "cups"),
         ing("guajillo chiles", 4.0, "whole"), ing("ancho chile", 1.0, "whole"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 4.0, "whole"),
         ing("chicken broth", 5.0, "cups"), ing("dried oregano", 1.0, "tsp"),
         ing("cumin", 0.5, "tsp"), ing("shredded cabbage", 1.0, "cup"),
         ing("radishes", 4.0, "whole"), ing("lime", 2.0, "whole"),
         ing("salt", 0.75, "tsp")],
        ["Simmer chicken in broth with half the onion for 25 minutes. Shred chicken.",
         "Toast dried chiles, soak in hot water for 15 minutes.",
         "Blend chiles with garlic, remaining onion, cumin, and soaking liquid.",
         "Strain sauce into the broth. Add hominy and shredded chicken.",
         "Simmer 20 minutes. Season with oregano and salt.",
         "Serve with cabbage, radishes, and lime wedges."],
        20, 50, "intermediate", 6,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free"],
        3, nutr(360, 30, 500, 460, 260)
    ))

    # 46. Grilled Tilapia with Cilantro-Lime Rice
    recipes.append(make_recipe(
        "Grilled Tilapia with Cilantro-Lime Rice",
        "Seasoned grilled tilapia served alongside fluffy cilantro-lime rice and black beans.",
        [ing("tilapia fillets", 1.0, "lb"), ing("long grain rice", 1.0, "cup"),
         ing("black beans", 1.0, "cup"), ing("lime juice", 3.0, "tbsp"),
         ing("fresh cilantro", 0.33, "cup"), ing("cumin", 1.0, "tsp"),
         ing("garlic powder", 0.5, "tsp"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("lime zest", 1.0, "tsp")],
        ["Cook rice according to package. Fluff and stir in chopped cilantro, lime juice, and zest.",
         "Season tilapia with cumin, garlic powder, salt, and olive oil.",
         "Grill fish for 3-4 minutes per side until flaky.",
         "Warm black beans in a small saucepan.",
         "Serve fish over cilantro-lime rice with beans on the side."],
        10, 20, "beginner", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free", "anti-inflammatory", "kidney-friendly"],
        4, nutr(390, 32, 340, 500, 270)
    ))

    # 47. Mexican Stuffed Sweet Potatoes
    recipes.append(make_recipe(
        "Mexican Stuffed Sweet Potatoes",
        "Baked sweet potatoes loaded with black beans, corn, avocado, and a cilantro-lime drizzle.",
        [ing("sweet potatoes", 4.0, "whole"), ing("black beans", 1.0, "cup"),
         ing("corn kernels", 0.5, "cup"), ing("avocado", 1.0, "whole"),
         ing("lime juice", 2.0, "tbsp"), ing("fresh cilantro", 0.25, "cup"),
         ing("cumin", 1.0, "tsp"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.25, "tsp"), ing("red onion", 0.25, "whole")],
        ["Bake sweet potatoes at 400°F for 45-50 minutes until very tender.",
         "Warm black beans with cumin and salt.",
         "Mix corn with diced red onion, cilantro, and lime juice.",
         "Split sweet potatoes and fluff the insides.",
         "Stuff with beans, corn mixture, and sliced avocado. Drizzle with olive oil."],
        10, 50, "beginner", 4,
        ["mexican", "dinner", "lunch", "gluten-free", "dairy-free", "vegan", "anti-inflammatory"],
        5, nutr(340, 12, 220, 680, 160)
    ))

    # 48. Shrimp Aguachile
    recipes.append(make_recipe(
        "Shrimp Aguachile",
        "Raw shrimp cured in a fiery lime-chile sauce with cucumber and red onion.",
        [ing("large shrimp", 1.0, "lb"), ing("lime juice", 0.75, "cup"),
         ing("serrano chile", 2.0, "whole"), ing("cucumber", 1.0, "whole"),
         ing("red onion", 0.5, "whole"), ing("fresh cilantro", 0.25, "cup"),
         ing("avocado", 1.0, "whole"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.5, "tsp")],
        ["Butterfly shrimp and lay flat on a plate.",
         "Blend lime juice, serrano chiles, cilantro stems, and salt until smooth.",
         "Pour sauce over shrimp and refrigerate for 20 minutes until shrimp turns opaque.",
         "Slice cucumber and red onion very thin.",
         "Arrange shrimp with cucumber and onion, top with avocado and cilantro leaves."],
        25, 0, "intermediate", 4,
        ["mexican", "lunch", "dinner", "gluten-free", "dairy-free", "anti-inflammatory", "low-sodium"],
        4, nutr(200, 24, 340, 380, 220)
    ))

    # 49. Aztec Soup (Sopa Azteca)
    recipes.append(make_recipe(
        "Sopa Azteca (Aztec Tortilla Soup)",
        "A smoky, rich tortilla soup with pasilla chiles and crispy tortilla strips.",
        [ing("chicken breast", 1.0, "lb"), ing("pasilla chile", 2.0, "whole"),
         ing("tomatillos", 0.5, "lb"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("chicken broth", 6.0, "cups"),
         ing("corn tortillas", 4, "pieces"), ing("avocado", 1.0, "whole"),
         ing("fresh cilantro", 0.25, "cup"), ing("olive oil", 2.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("lime", 1.0, "whole")],
        ["Toast pasilla chiles in a dry pan. Soak in hot water for 10 minutes.",
         "Roast tomatillos, onion, and garlic. Blend with soaked chiles.",
         "Simmer chicken in broth for 20 minutes, shred.",
         "Add blended sauce to broth with chicken. Simmer 15 minutes.",
         "Cut tortillas into strips and bake until crispy.",
         "Serve soup with tortilla strips, avocado, cilantro, and lime."],
        15, 40, "intermediate", 4,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free"],
        4, nutr(310, 28, 440, 460, 240)
    ))

    # 50. Enfrijoladas
    recipes.append(make_recipe(
        "Enfrijoladas",
        "Corn tortillas dipped in a silky black bean sauce, filled with crumbled cheese and onion.",
        [ing("corn tortillas", 8, "pieces"), ing("black beans", 2.0, "cups"),
         ing("onion", 0.5, "whole"), ing("garlic cloves", 2.0, "whole"),
         ing("chicken broth", 0.5, "cup"), ing("avocado", 1.0, "whole"),
         ing("crumbled queso fresco", 0.5, "cup"), ing("fresh cilantro", 0.25, "cup"),
         ing("olive oil", 1.0, "tbsp"), ing("salt", 0.5, "tsp"),
         ing("cumin", 0.5, "tsp")],
        ["Blend black beans with broth, sautéed onion, garlic, cumin, and salt until smooth.",
         "Heat bean sauce in a wide pan until simmering.",
         "Dip tortillas briefly in the warm bean sauce to soften.",
         "Fill with a little queso and onion, fold into thirds.",
         "Arrange on plates, spoon more sauce over, top with avocado and cilantro."],
        15, 15, "beginner", 4,
        ["mexican", "dinner", "lunch", "gluten-free"],
        4, nutr(360, 18, 400, 560, 200)
    ))

    # 51. Picadillo
    recipes.append(make_recipe(
        "Mexican Picadillo",
        "A savory-sweet ground beef hash with potatoes, carrots, and warm spices.",
        [ing("ground beef", 1.0, "lb"), ing("potatoes", 2.0, "whole"),
         ing("carrots", 2.0, "whole"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 2.0, "whole"), ing("cumin", 1.0, "tsp"),
         ing("dried oregano", 0.5, "tsp"), ing("olive oil", 1.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("fresh cilantro", 0.25, "cup"),
         ing("corn tortillas", 8, "pieces")],
        ["Brown ground beef in olive oil, breaking into small pieces. Drain excess fat.",
         "Add diced onion and garlic, cook until softened.",
         "Add diced potatoes and carrots, cumin, oregano, and salt.",
         "Add a splash of water, cover, and simmer for 20 minutes until vegetables are tender.",
         "Serve with warm corn tortillas and cilantro."],
        15, 25, "beginner", 6,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(380, 24, 400, 540, 230)
    ))

    # 52. Cochinita Pibil-Style Pork
    recipes.append(make_recipe(
        "Cochinita Pibil-Style Pork",
        "Yucatecan slow-roasted pork marinated in citrus and achiote, served with pickled onion.",
        [ing("pork shoulder", 2.0, "lb"), ing("achiote paste", 3.0, "tbsp"),
         ing("orange juice", 0.75, "cup"), ing("lime juice", 2.0, "tbsp"),
         ing("garlic cloves", 4.0, "whole"), ing("cumin", 1.0, "tsp"),
         ing("dried oregano", 0.5, "tsp"), ing("red onion", 1.0, "whole"),
         ing("apple cider vinegar", 0.25, "cup"), ing("salt", 1.0, "tsp"),
         ing("banana leaves", 2.0, "pieces"), ing("corn tortillas", 8, "pieces")],
        ["Blend achiote paste with orange juice, lime juice, garlic, cumin, oregano, and salt.",
         "Marinate pork in the mixture for at least 2 hours or overnight.",
         "Wrap pork in banana leaves, place in a Dutch oven.",
         "Braise at 300°F for 3.5 hours until fall-apart tender.",
         "Quick-pickle sliced red onion in vinegar with salt.",
         "Shred pork and serve in tortillas with pickled onion."],
        30, 210, "advanced", 8,
        ["mexican", "dinner", "gluten-free", "dairy-free"],
        3, nutr(380, 32, 420, 440, 250)
    ))

    # 53. Green Enchilada Soup
    recipes.append(make_recipe(
        "Green Enchilada Soup",
        "A creamy and tangy soup with all the flavors of enchiladas verdes in a comforting bowl.",
        [ing("chicken breast", 1.0, "lb"), ing("tomatillos", 0.75, "lb"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("chicken broth", 5.0, "cups"), ing("coconut cream", 0.5, "cup"),
         ing("cumin", 1.0, "tsp"), ing("dried oregano", 0.5, "tsp"),
         ing("corn tortillas", 4, "pieces"), ing("avocado", 1.0, "whole"),
         ing("fresh cilantro", 0.25, "cup"), ing("lime juice", 2.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("olive oil", 1.0, "tbsp")],
        ["Roast tomatillos, onion, and garlic under the broiler until charred.",
         "Simmer chicken in broth for 20 minutes, then shred.",
         "Blend roasted vegetables with a cup of broth until smooth.",
         "Add green sauce to the pot with remaining broth, cumin, oregano, and salt.",
         "Stir in coconut cream and shredded chicken. Simmer 10 minutes.",
         "Serve with crispy tortilla strips, avocado, cilantro, and lime."],
        15, 35, "intermediate", 6,
        ["mexican", "dinner", "soup", "gluten-free", "dairy-free"],
        4, nutr(330, 28, 440, 500, 250)
    ))

    # 54. Camarones al Mojo de Ajo
    recipes.append(make_recipe(
        "Camarones al Mojo de Ajo",
        "Succulent shrimp sautéed in a buttery garlic sauce with lime, a Mexican coastal classic.",
        [ing("large shrimp", 1.5, "lb"), ing("garlic cloves", 10.0, "whole"),
         ing("olive oil", 3.0, "tbsp"), ing("lime juice", 3.0, "tbsp"),
         ing("dried chile de arbol", 2.0, "whole"), ing("fresh cilantro", 0.25, "cup"),
         ing("salt", 0.5, "tsp"), ing("white rice", 2.0, "cups")],
        ["Slice garlic cloves thinly. Cook very slowly in olive oil over low heat until golden and crispy.",
         "Remove garlic chips and set aside. Increase heat to medium-high.",
         "Add shrimp and dried chiles to the garlic oil. Cook 2-3 minutes per side.",
         "Squeeze lime juice over shrimp and toss with garlic chips.",
         "Serve over rice with cilantro and extra lime."],
        15, 15, "intermediate", 4,
        ["mexican", "dinner", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(380, 32, 380, 400, 270)
    ))

    # 55. Mexican Lentil Soup
    recipes.append(make_recipe(
        "Mexican Lentil Soup (Sopa de Lentejas)",
        "A humble and nourishing lentil soup with cumin, cilantro, and a squeeze of lime.",
        [ing("brown lentils", 1.5, "cups"), ing("onion", 1.0, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("carrots", 2.0, "whole"),
         ing("cumin", 1.5, "tsp"), ing("dried oregano", 0.5, "tsp"),
         ing("vegetable broth", 6.0, "cups"), ing("olive oil", 2.0, "tbsp"),
         ing("lime juice", 2.0, "tbsp"), ing("fresh cilantro", 0.25, "cup"),
         ing("salt", 0.75, "tsp")],
        ["Sauté diced onion, garlic, and carrots in olive oil until softened.",
         "Add lentils, cumin, oregano, and salt. Stir for a minute.",
         "Pour in broth, bring to a boil, then reduce heat and simmer 30 minutes.",
         "Lentils should be very tender. Mash some against the side of the pot for thickness.",
         "Stir in lime juice, serve topped with cilantro."],
        10, 35, "beginner", 6,
        ["mexican", "lunch", "dinner", "soup", "gluten-free", "dairy-free", "vegan", "anti-inflammatory"],
        4, nutr(280, 18, 380, 540, 200)
    ))

    return recipes


def get_mediterranean_recipes():
    recipes = []

    # 1. Shakshuka (AIP Adapted - No Nightshades)
    recipes.append(make_recipe(
        "AIP Shakshuka with Beet Sauce",
        "A nightshade-free take on shakshuka using roasted beet sauce with poached eggs and fresh herbs.",
        [ing("beets", 3.0, "whole"), ing("eggs", 4.0, "whole"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("cumin", 1.5, "tsp"), ing("turmeric", 0.5, "tsp"),
         ing("olive oil", 2.0, "tbsp"), ing("fresh parsley", 0.25, "cup"),
         ing("salt", 0.5, "tsp"), ing("lemon juice", 1.0, "tbsp")],
        ["Roast beets at 400°F wrapped in foil for 45 minutes. Peel and blend until smooth.",
         "Sauté diced onion and garlic in olive oil until softened.",
         "Add beet puree, cumin, turmeric, and salt. Simmer 10 minutes.",
         "Make 4 wells in the sauce and crack an egg into each.",
         "Cover and cook for 6-8 minutes until egg whites are set but yolks are runny.",
         "Garnish with parsley and lemon juice."],
        15, 60, "intermediate", 2,
        ["mediterranean", "breakfast", "gluten-free", "dairy-free", "anti-inflammatory"],
        5, nutr(280, 16, 380, 600, 200)
    ))

    # 2. Greek Lemon Chicken
    recipes.append(make_recipe(
        "Greek Lemon Chicken with Potatoes",
        "Roasted chicken pieces with crispy potatoes in a bright lemon-oregano sauce.",
        [ing("chicken thighs", 2.0, "lb"), ing("potatoes", 1.5, "lb"),
         ing("lemon juice", 0.33, "cup"), ing("olive oil", 3.0, "tbsp"),
         ing("garlic cloves", 5.0, "whole"), ing("dried oregano", 2.0, "tsp"),
         ing("chicken broth", 0.75, "cup"), ing("salt", 0.75, "tsp"),
         ing("black pepper", 0.5, "tsp"), ing("fresh parsley", 0.25, "cup")],
        ["Cut potatoes into wedges and arrange in a roasting pan.",
         "Whisk lemon juice, olive oil, minced garlic, oregano, broth, salt, and pepper.",
         "Nestle chicken thighs among the potatoes. Pour lemon sauce over everything.",
         "Roast at 425°F for 50 minutes, basting halfway, until chicken is golden.",
         "Garnish with parsley and serve with pan juices."],
        15, 50, "intermediate", 6,
        ["mediterranean", "dinner", "gluten-free", "dairy-free"],
        4, nutr(440, 34, 480, 680, 300)
    ))

    # 3. Falafel Bowls
    recipes.append(make_recipe(
        "Baked Falafel Bowls",
        "Crispy baked chickpea falafel served in bowls with greens, cucumber, and tahini dressing.",
        [ing("canned chickpeas", 2.0, "cups"), ing("fresh parsley", 0.5, "cup"),
         ing("onion", 0.5, "whole"), ing("garlic cloves", 3.0, "whole"),
         ing("cumin", 1.5, "tsp"), ing("coriander", 1.0, "tsp"),
         ing("olive oil", 3.0, "tbsp"), ing("mixed greens", 4.0, "cups"),
         ing("cucumber", 1.0, "whole"), ing("tahini", 3.0, "tbsp"),
         ing("lemon juice", 2.0, "tbsp"), ing("salt", 0.5, "tsp")],
        ["Pulse chickpeas, parsley, onion, garlic, cumin, coriander, and salt in a food processor until coarsely ground.",
         "Form into small patties and place on an oiled baking sheet.",
         "Bake at 400°F for 25 minutes, flipping halfway, until golden and crispy.",
         "Whisk tahini with lemon juice and water until smooth for dressing.",
         "Assemble bowls with greens, sliced cucumber, falafel, and tahini drizzle."],
        20, 25, "intermediate", 4,
        ["mediterranean", "lunch", "dinner", "gluten-free", "dairy-free", "vegan"],
        4, nutr(380, 16, 380, 480, 220)
    ))

    # 4. Hummus Power Bowl
    recipes.append(make_recipe(
        "Mediterranean Hummus Power Bowl",
        "A nourishing bowl built around creamy hummus with roasted vegetables and grains.",
        [ing("canned chickpeas", 1.5, "cups"), ing("tahini", 3.0, "tbsp"),
         ing("lemon juice", 3.0, "tbsp"), ing("garlic clove", 1.0, "whole"),
         ing("quinoa", 1.0, "cup"), ing("cucumber", 1.0, "whole"),
         ing("cherry tomatoes", 1.0, "cup"), ing("kalamata olives", 0.25, "cup"),
         ing("olive oil", 3.0, "tbsp"), ing("fresh parsley", 0.25, "cup"),
         ing("salt", 0.5, "tsp"), ing("cumin", 0.5, "tsp")],
        ["Blend chickpeas, tahini, lemon juice, garlic, cumin, salt, and olive oil until very smooth.",
         "Cook quinoa according to package directions and let cool slightly.",
         "Dice cucumber and halve cherry tomatoes.",
         "Spoon hummus into bowls. Top with quinoa, vegetables, and olives.",
         "Drizzle with olive oil and garnish with parsley."],
        15, 15, "beginner", 4,
        ["mediterranean", "lunch", "dinner", "gluten-free", "dairy-free", "vegan"],
        3, nutr(440, 18, 420, 540, 250)
    ))

    # 5. Lamb Kofta
    recipes.append(make_recipe(
        "Lamb Kofta with Herb Yogurt",
        "Spiced ground lamb kebabs grilled on skewers with a cool herbed yogurt sauce.",
        [ing("ground lamb", 1.5, "lb"), ing("onion", 0.5, "whole"),
         ing("garlic cloves", 3.0, "whole"), ing("cumin", 1.5, "tsp"),
         ing("coriander", 1.0, "tsp"), ing("fresh parsley", 0.25, "cup"),
         ing("fresh mint", 2.0, "tbsp"), ing("coconut yogurt", 0.75, "cup"),
         ing("lemon juice", 2.0, "tbsp"), ing("cucumber", 0.5, "whole"),
         ing("olive oil", 1.0, "tbsp"), ing("salt", 0.75, "tsp")],
        ["Mix ground lamb with grated onion, garlic, cumin, coriander, parsley, and salt.",
         "Shape into oval kofta around skewers.",
         "Grill over medium-high heat for 4-5 minutes per side until cooked through.",
         "Mix coconut yogurt with diced cucumber, mint, lemon juice, and a pinch of salt.",
         "Serve kofta with herb yogurt sauce."],
        20, 12, "intermediate", 4,
        ["mediterranean", "dinner", "gluten-free"],
        3, nutr(380, 28, 400, 420, 260)
    ))

    # 6. Grilled Mediterranean Fish with Herbs
    recipes.append(make_recipe(
        "Grilled Mediterranean Fish with Herbs",
        "Whole grilled sea bass or branzino with lemon, fresh herbs, and olive oil.",
        [ing("sea bass fillets", 1.5, "lb"), ing("lemon", 2.0, "whole"),
         ing("fresh rosemary", 3.0, "sprigs"), ing("fresh thyme", 4.0, "sprigs"),
         ing("garlic cloves", 4.0, "whole"), ing("olive oil", 3.0, "tbsp"),
         ing("capers", 1.0, "tbsp"), ing("fresh parsley", 0.25, "cup"),
         ing("salt", 0.5, "tsp"), ing("mixed greens", 4.0, "cups")],
        ["Score fish fillets with shallow diagonal cuts.",
         "Rub with olive oil, salt, and minced garlic. Tuck herb sprigs alongside.",
         "Grill over medium heat for 5-6 minutes per side until fish flakes easily.",
         "Squeeze lemon juice over fish and scatter capers on top.",
         "Serve on a bed of mixed greens with extra lemon wedges."],
        10, 12, "intermediate", 4,
        ["mediterranean", "dinner", "gluten-free", "dairy-free", "anti-inflammatory", "low-sodium", "kidney-friendly"],
        5, nutr(300, 38, 340, 520, 280)
    ))

    # 7. Cauliflower Rice Tabbouleh
    recipes.append(make_recipe(
        "Cauliflower Rice Tabbouleh",
        "A grain-free take on classic tabbouleh using riced cauliflower, packed with fresh herbs and lemon.",
        [ing("cauliflower", 1.0, "head"), ing("fresh parsley", 2.0, "cups"),
         ing("fresh mint", 0.5, "cup"), ing("cucumber", 1.0, "whole"),
         ing("green onions", 4.0, "whole"), ing("lemon juice", 0.25, "cup"),
         ing("olive oil", 3.0, "tbsp"), ing("salt", 0.5, "tsp"),
         ing("cherry tomatoes", 0.5, "cup")],
        ["Pulse cauliflower in a food processor until rice-sized. Spread on a towel and squeeze dry.",
         "Finely chop parsley, mint, cucumber, and green onions.",
         "Toss cauliflower rice with herbs, cucumber, and halved cherry tomatoes.",
         "Dress with lemon juice, olive oil, and salt.",
         "Let sit 10 minutes for flavors to meld before serving."],
        20, 0, "beginner", 4,
        ["mediterranean", "lunch", "side", "gluten-free", "dairy-free", "vegan", "low-sodium", "kidney-friendly", "anti-inflammatory"],
        5, nutr(140, 5, 180, 420, 80)
    ))

    # 8. Stuffed Grape Leaves (Dolmas)
    recipes.append(make_recipe(
        "Stuffed Grape Leaves (Dolmas)",
        "Tender grape leaves filled with herbed rice, pine nuts, and lemon, served warm or cold.",
        [ing("grape leaves", 30, "pieces"), ing("long grain rice", 1.0, "cup"),
         ing("onion", 1.0, "whole"), ing("pine nuts", 0.25, "cup"),
         ing("fresh dill", 0.25, "cup"), ing("fresh mint", 0.25, "cup"),
         ing("lemon juice", 3.0, "tbsp"), ing("olive oil", 3.0, "tbsp"),
         ing("salt", 0.5, "tsp"), ing("water", 2.0, "cups")],
        ["Sauté diced onion in olive oil. Add rice and toast 2 minutes.",
         "Stir in pine nuts, dill, mint, lemon juice, and salt. Let cool.",
         "Lay a grape leaf flat, place a spoonful of filling near the stem end.",
         "Fold sides in and roll tightly. Arrange snugly in a pot.",
         "Add water, weight with a plate, and simmer 45 minutes until rice is tender.",
         "Serve warm or at room temperature with extra lemon."],
        30, 50, "advanced", 6,
        ["mediterranean", "side", "lunch", "gluten-free", "dairy-free", "vegan"],
        4, nutr(180, 4, 280, 200, 80)
    ))

    # 9. Moroccan Chicken Tagine
    recipes.append(make_recipe(
        "Moroccan Chicken Tagine with Preserved Lemon",
        "A fragrant slow-cooked chicken stew with olives, preserved lemon, and warm spices.",
        [ing("chicken thighs", 2.0, "lb"), ing("onion", 2.0, "whole"),
         ing("garlic cloves", 4.0, "whole"), ing("preserved lemon", 1.0, "whole"),
         ing("green olives", 0.5, "cup"), ing("fresh cilantro", 0.5, "cup"),
         ing("ground ginger", 1.0, "tsp"), ing("turmeric", 1.0, "tsp"),
         ing("cinnamon", 0.5, "tsp"), ing("saffron threads", 0.25, "tsp"),
         ing("olive oil", 2.0, "tbsp"), ing("chicken broth", 1.0, "cup"),
         ing("salt", 0.5, "tsp")],
        ["Season chicken with ginger, turmeric, cinnamon, saffron, and salt.",
         "Brown chicken in olive oil, then remove.",
         "Sauté sliced onions and garlic until very soft and golden.",
         "Return chicken, add broth, chopped preserved lemon, and olives.",
         "Cover and simmer for 40 minutes until chicken is very tender.",
         "Garnish with fresh cilantro and serve with couscous or rice."],
        15, 50, "intermediate", 6,
        ["mediterranean", "dinner", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(400, 34, 520, 480, 280)
    ))

    # 10. Baba Ganoush Bowls
    recipes.append(make_recipe(
        "Baba Ganoush Bowl",
        "Smoky roasted eggplant dip served as a bowl base with grilled chicken, veggies, and herbs.",
        [ing("eggplant", 2.0, "whole"), ing("chicken breast", 1.0, "lb"),
         ing("tahini", 2.0, "tbsp"), ing("lemon juice", 3.0, "tbsp"),
         ing("garlic cloves", 2.0, "whole"), ing("cucumber", 1.0, "whole"),
         ing("cherry tomatoes", 1.0, "cup"), ing("olive oil", 3.0, "tbsp"),
         ing("fresh parsley", 0.25, "cup"), ing("salt", 0.5, "tsp"),
         ing("cumin", 0.5, "tsp"), ing("mixed greens", 2.0, "cups")],
        ["Char whole eggplants over a flame or under the broiler until collapsed and smoky.",
         "Scoop out flesh and mash with tahini, lemon juice, garlic, cumin, and salt.",
         "Season chicken with olive oil and salt. Grill for 6 minutes per side and slice.",
         "Dice cucumber and halve cherry tomatoes.",
         "Spoon baba ganoush into bowls, top with greens, chicken, and vegetables.",
         "Drizzle with olive oil and garnish with parsley."],
        15, 25, "intermediate", 4,
        ["mediterranean", "lunch", "dinner", "gluten-free", "dairy-free", "anti-inflammatory"],
        4, nutr(380, 32, 380, 560, 250)
    ))

    # 11. Mediterranean Grain Bowl
    recipes.append(make_recipe(
        "Mediterranean Grain Bowl with Lemon Vinaigrette",
        "A colorful grain bowl with farro, roasted vegetables, olives, and a bright lemon dressing.",
        [ing("farro", 1.0, "cup"), ing("zucchini", 1.0, "whole"),
         ing("red onion", 0.5, "whole"), ing("cherry tomatoes", 1.0, "cup"),
         ing("kalamata olives", 0.25, "cup"), ing("cucumber", 1.0, "whole"),
         ing("lemon juice", 3.0, "tbsp"), ing("olive oil", 3.0, "tbsp"),
         ing("fresh basil", 0.25, "cup"), ing("garlic clove", 1.0, "whole"),
         ing("salt", 0.5, "tsp"), ing("dried oregano", 0.5, "tsp")],
        ["Cook farro in salted water for 25 minutes until tender. Drain and cool.",
         "Toss sliced zucchini and red onion with olive oil. Roast at 425°F for 20 minutes.",
         "Whisk lemon juice, olive oil, minced garlic, oregano, and salt for dressing.",
         "Combine farro, roasted vegetables, halved tomatoes, diced cucumber, and olives.",
         "Toss with dressing and top with fresh basil."],
        10, 30, "beginner", 4,
        ["mediterranean", "lunch", "dinner", "dairy-free", "vegan"],
        4, nutr(340, 10, 350, 400, 180)
    ))

    # 12. Spanakopita-Inspired Bowl
    recipes.append(make_recipe(
        "Spanakopita-Inspired Spinach Rice Bowl",
        "All the flavors of spanakopita in a bowl — spinach, dill, lemon, and feta over rice.",
        [ing("fresh spinach", 6.0, "cups"), ing("long grain rice", 1.0, "cup"),
         ing("onion", 1.0, "whole"), ing("garlic cloves", 2.0, "whole"),
         ing("fresh dill", 0.25, "cup"), ing("lemon juice", 2.0, "tbsp"),
         ing("olive oil", 2.0, "tbsp"), ing("feta cheese", 0.5, "cup"),
         ing("pine nuts", 2.0, "tbsp"), ing("salt", 0.5, "tsp"),
         ing("egg", 1.0, "whole")],
        ["Cook rice and set aside.",
         "Sauté diced onion and garlic in olive oil until softened.",
         "Add spinach and wilt completely. Stir in dill and lemon juice.",
         "Beat egg and fold into the warm spinach mixture off heat.",
         "Serve spinach mixture over rice, topped with crumbled feta and toasted pine nuts."],
        10, 20, "beginner", 4,
        ["mediterranean", "lunch", "dinner"],
        3, nutr(360, 14, 420, 480, 200)
    ))

    return recipes


def main():
    with open(SEED_FILE) as f:
        recipes = json.load(f)

    existing_names = {r["name"] for r in recipes}

    # Count current cuisines
    mexican_count = sum(1 for r in recipes if "mexican" in r.get("tags", []))
    med_count = sum(1 for r in recipes if "mediterranean" in r.get("tags", []))
    print(f"Current totals: {len(recipes)} recipes, {mexican_count} Mexican, {med_count} Mediterranean")

    new_mexican = get_mexican_recipes()
    new_med = get_mediterranean_recipes()

    added_mex = 0
    added_med = 0
    skipped = []

    for r in new_mexican:
        if r["name"] in existing_names:
            skipped.append(r["name"])
            continue
        recipes.append(r)
        existing_names.add(r["name"])
        added_mex += 1

    for r in new_med:
        if r["name"] in existing_names:
            skipped.append(r["name"])
            continue
        recipes.append(r)
        existing_names.add(r["name"])
        added_med += 1

    # Final counts
    total = len(recipes)
    final_mex = sum(1 for r in recipes if "mexican" in r.get("tags", []))
    final_med = sum(1 for r in recipes if "mediterranean" in r.get("tags", []))

    print(f"\nAdded {added_mex} Mexican recipes, {added_med} Mediterranean recipes")
    if skipped:
        print(f"Skipped (duplicate names): {skipped}")
    print(f"\nFinal totals: {total} recipes")
    print(f"  Mexican: {final_mex} ({final_mex/total*100:.1f}%)")
    print(f"  Mediterranean: {final_med} ({final_med/total*100:.1f}%)")

    with open(SEED_FILE, "w") as f:
        json.dump(recipes, f, indent=2)
    print(f"\nWrote {total} recipes to {SEED_FILE}")


if __name__ == "__main__":
    main()

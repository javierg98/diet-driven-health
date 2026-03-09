from app.models.food_entry import FoodEntry


def test_create_food_entry(db):
    entry = FoodEntry(
        user_id=1,
        description="Salmon with rice and steamed broccoli",
        dish_name="Salmon with rice",
        detected_ingredients=["salmon", "rice", "broccoli"],
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.id is not None
    assert entry.dish_name == "Salmon with rice"
    assert entry.detected_ingredients == ["salmon", "rice", "broccoli"]
    assert entry.created_at is not None

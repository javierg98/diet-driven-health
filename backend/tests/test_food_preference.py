from app.models.food_preference import FoodPreference


def test_create_like_preference(db):
    pref = FoodPreference(
        user_id=1,
        type="like",
        value="thai curry",
        category="cuisine",
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    assert pref.id is not None
    assert pref.type == "like"
    assert pref.value == "thai curry"
    assert pref.category == "cuisine"
    assert pref.created_at is not None


def test_create_dislike_preference(db):
    pref = FoodPreference(
        user_id=1,
        type="dislike",
        value="cilantro",
        category="ingredient",
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    assert pref.type == "dislike"
    assert pref.category == "ingredient"

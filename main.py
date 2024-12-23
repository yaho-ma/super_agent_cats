from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

import my_models
from database import SessionLocal, engine
from my_models import Cat
from pydantic_model import CatSchema, UpdateSalaryRequest, MissionSchema, TargetSchema, UpdateTargetSchema
from get_valid_breeds import fetch_valid_breeds

app = FastAPI(
    title="Cat Villan Agency"
)

my_models.Base.metadata.create_all(bind=engine)


def get_database():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# == endpoints == ########################################################################


@app.post("/cats", response_model=CatSchema)
async def create_cat(cat: CatSchema, db: Session = Depends(get_database)):
    valid_breeds_list = await fetch_valid_breeds()

    if cat.breed not in valid_breeds_list:
        raise HTTPException(
            status_code=400,
            detail=f"The breed is invalid.\n\n"
                   f" Allowed breeds are: {', '.join(valid_breeds_list)}"
        )

    cat_model = my_models.Cat()

    cat_model.name = cat.name
    cat_model.years_of_experience = cat.years_of_experience
    cat_model.breed = cat.breed
    cat_model.salary = cat.salary

    # add to db
    db.add(cat_model)
    db.commit()
    return cat


@app.get("/cats", response_model=List[CatSchema])
def get_all_cats(db: Session = Depends(get_database)):
    return db.query(my_models.Cat).all()


@app.delete("/cats/{cat_id}")
def remove_cat(cat_id: int, db: Session = Depends(get_database)):
    cat_model = db.query(my_models.Cat).filter(my_models.Cat.id == cat_id).first()

    if cat_model is None:
        raise HTTPException(
            status_code=404,
            detail=f'cat with ID {cat_id} does not exist')

    db.query(my_models.Cat).filter(my_models.Cat.id == cat_id).delete()
    db.commit()

    return {"detail": f"Cat with ID {cat_id} was removed successfully."}


@app.put("/cats/{cat_id}")
def update_salary_for_cat(cat_id: int,
                          request: UpdateSalaryRequest,
                          db: Session = Depends(get_database)
                          ):
    cat_model = db.query(my_models.Cat).filter(my_models.Cat.id == cat_id).first()

    if cat_model is None:
        raise HTTPException(
            status_code=404,
            detail=f'cat with ID {cat_id} does not exist')

    cat_model.salary = request.salary
    db.commit()

    return {f"sarary for cat with ID: {cat_id} has been updated to: {cat_model.salary}"}


@app.get("/cats/{cat_id}")
def get_one_cat(
        cat_id: int,
        db: Session = Depends(get_database)

):
    cat_model = db.query(my_models.Cat).filter(my_models.Cat.id == cat_id).first()
    if cat_model is None:
        raise HTTPException(
            status_code=404, detail=f"Spy cat with ID {cat_id} does not exist"
        )
    return cat_model


# -- mission endpoint -- ####################################################################


@app.post("/mission", response_model=MissionSchema)
def create_mission(mission: MissionSchema,
                   db: Session = Depends(get_database)):
    if mission.cat_id:
        cat = db.query(my_models.Cat).filter(my_models.Cat.id == mission.cat_id).first()

        if not cat:
            raise HTTPException(
                status_code=404,
                detail=f"Cat with ID {mission.cat_id} does not exist")

    mission_model = my_models.Mission(cat_id=mission.cat_id, complete=mission.complete)

    for target in mission.targets:
        target_model = my_models.Target(
            name=target.name,
            country=target.country,
            notes=target.notes,
            complete=target.complete
        )
        mission_model.targets.append(target_model)

    db.add(mission_model)
    db.commit()

    return mission_model


@app.delete("/mission/{mission_id}")
def delete_mission(mission_id: int, db: Session = Depends(get_database)):
    # get the mission
    mission_model = db.query(my_models.Mission).filter(my_models.Mission.id == mission_id).first()

    if mission_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"Mission with ID {mission_id} does not exist"
        )

    # Check if the mission is assigned to a cat
    if mission_model.cat_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Mission cannot be deleted because it is assigned to a cat"
        )

    # Delete the mission
    db.query(my_models.Mission).filter(my_models.Mission.id == mission_id).delete()
    db.commit()

    return {"detail": f"Mission with ID {mission_id} has been deleted successfully"}


@app.put("/targets/{target_id}")
def update_target(
        target_id: int,
        updates: UpdateTargetSchema,
        db: Session = Depends(get_database)
):
    # get the target
    target = db.query(my_models.Target).filter(my_models.Target.id == target_id).first()

    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"Target with ID {target_id} does not exist"
        )

    # get the associated mission
    mission = db.query(my_models.Mission).filter(my_models.Mission.id == target.mission_id).first()

    # Check if the mission or target is completed
    if updates.notes and (target.complete or mission.complete):
        raise HTTPException(
            status_code=400,
            detail="Notes cannot be updated if the target or mission is completed."
        )

    # updating the fields
    if updates.name is not None:
        target.name = updates.name

    if updates.country is not None:
        target.country = updates.country

    if updates.notes is not None:
        target.notes = updates.notes

    if updates.complete is not None:
        target.complete = updates.complete


    db.commit()

    return {"detail": f"Target with ID {target_id} updated successfully"}


@app.put("/missions/{mission_id}/assign_cat/{cat_id}", response_model=MissionSchema)
def assign_cat_to_mission(mission_id: int,
                          cat_id: int,
                          db: Session = Depends(get_database)
                          ):
    # Check if the mission exists
    mission = db.query(my_models.Mission).filter(my_models.Mission.id == mission_id).first()

    if mission is None:
        raise HTTPException(status_code=404, detail=f"Mission with ID {mission_id} does not exist")

    # Check if the cat exists
    cat = db.query(my_models.Cat).filter(my_models.Cat.id == cat_id).first()

    if cat is None:
        raise HTTPException(status_code=404, detail=f"Cat with ID {cat_id} does not exist")

    # connect the cat with the mission
    mission.cat_id = cat_id
    db.commit()
    db.refresh(mission)

    return mission


@app.get("/missions", response_model=List[MissionSchema])
def get_all_missions(db: Session = Depends(get_database)):
    missions = db.query(my_models.Mission).all()

    return missions


@app.get("/missions/{mission_id}", response_model=MissionSchema)
def get_mission_by_id(mission_id: int,
                      db: Session = Depends(get_database)
                      ):
    mission = db.query(my_models.Mission).filter(my_models.Mission.id == mission_id).first()

    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission with ID {mission_id} not found")

    return mission

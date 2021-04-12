# standoff2conll
Conversion from brat-flavored standoff to CoNLL format

## Usage
```
> python standoff2spert.py {PATH_TO_DATASET}\train
```

```
> python standoff2spert.py {PATH_TO_DATASET}\train {PATH_TO_DATASET}\dev {PATH_TO_DATASET}\test
```

```
> python standoff2spert.py {PATH_TO_DATASET}\train {PATH_TO_DATASET}\dev {PATH_TO_DATASET}\test --exclude PLACE_OF_DEATH SCHOOLS_ATTENDED DATE_DEFUNCT_IN AGENT OWNER_OF MEMBER_OF DATE_OF_CREATION
```

It produces "nerel_all.json" file in each folder

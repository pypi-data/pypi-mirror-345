from finessensual.expenditures import ExpenditureType, ExpenditurePhase
from finessensual.costs import SalaryCost, OperationCost

def create_salary_views( data: dict[ str, SalaryCost ],
                         view: dict ):
    view['by_project'] = {}
    view['by_date'] = {}
    for key, salary in data.items():
        # view by project: view->projectnr->date->personnr->[all keys]
        if salary.projectnr not in view['by_project']:
            view['by_project'][salary.projectnr] = {}
        if salary.date not in view['by_project'][salary.projectnr]:
            view['by_project'][salary.projectnr][salary.date] = {}
        if salary.personnr not in view['by_project'][salary.projectnr][salary.date]:
            view['by_project'][salary.projectnr][salary.date][salary.personnr] = []
        view['by_project'][salary.projectnr][salary.date][salary.personnr].append( key )

        # view by person: view->date->person->project->key
        if salary.date not in view['by_date']:
            view['by_date'][salary.date] = {}
        if salary.personnr not in view['by_date'][salary.date]:
            view['by_date'][salary.date][salary.personnr] = {}
        view['by_date'][salary.date][salary.personnr][salary.projectnr] = key
        
def create_eqpoprovh_views( data: dict,
                               view: dict ):
    view['by_project'] = {}
    for key, cost in data.items():
        # view by project: view->projectnr->data->cost
        if cost.projectnr not in view['by_project']:
            view['by_project'][cost.projectnr] = {}
        if cost.date not in view['by_project'][cost.projectnr]:
            view['by_project'][cost.projectnr][cost.date] = []
        view['by_project'][cost.projectnr][cost.date].append( key )


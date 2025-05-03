import openmdao.api as om
from pytest import approx

from h2integrate.core.finances import ProFastComp


def test_electrolyzer_refurb_results():
    plant_config = {
        "finance_parameters": {
            "profast_general_inflation": 0.02,
            "costing_general_inflation": 0.0,
            "sales_tax_rate": 0.07,
            "property_tax": 0.01,
            "property_insurance": 0.005,
            "administrative_expense_percent_of_sales": 0.03,
            "total_income_tax_rate": 0.21,
            "capital_gains_tax_rate": 0.15,
            "discount_rate": 0.08,
            "debt_equity_split": 70,
            "debt_equity_ratio": None,
            "debt_type": "Revolving debt",
            "loan_period": 10,
            "debt_interest_rate": 0.05,
            "cash_onhand_months": 6,
            "depreciation_method": "Straight line",
            "depreciation_period": 20,
            "depreciation_period_electrolyzer": 10,
        },
        "plant": {
            "atb_year": 2022,
            "plant_life": 30,
            "installation_time": 24,
            "cost_year": 2022,
            "grid_connection": True,
            "ppa_price": 0.05,
        },
        "policy_parameters": {
            "electricity_itc": 0.3,
            "h2_storage_itc": 0.3,
            "electricity_ptc": 25,
            "h2_ptc": 3,
        },
    }

    tech_config = {
        "electrolyzer": {
            "model_inputs": {
                "financial_parameters": {
                    "replacement_cost_percent": 0.1,
                }
            }
        },
    }

    prob = om.Problem()
    comp = ProFastComp(plant_config=plant_config, tech_config=tech_config)
    prob.model.add_subsystem("comp", comp, promotes=["*"])

    prob.setup()

    prob.set_val("capex_adjusted_electrolyzer", 1.0e7, units="USD")
    prob.set_val("opex_adjusted_electrolyzer", 1.0e4, units="USD/year")

    prob.set_val("total_hydrogen_produced", 4.0e5, units="kg/year")
    prob.set_val("time_until_replacement", 5.0e3, units="h")

    prob.run_model()

    assert prob["LCOH"] == approx(4.27529137)

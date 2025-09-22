/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class MealSelectionWidget extends Component {
    static template = "event_management.MealSelectionWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            selectedMeals: [],
            meatFilter: null,
            totalCost: 0
        });
    }

    async selectMealPackage(mealId) {
        if (!this.props.record?.resId) return;
        try {
            await this.orm.write("event.booking", [this.props.record.resId], {
                selected_meal_packages: [[4, mealId]]
            });
            await this.props.record.load();
            this.notification.add("Meal package added!", { type: "success" });
        } catch (error) {
            this.notification.add("Error adding meal package", { type: "danger" });
        }
    }

    async removeMealPackage(mealId) {
        if (!this.props.record?.resId) return;
        try {
            await this.orm.write("event.booking", [this.props.record.resId], {
                selected_meal_packages: [[3, mealId]]
            });
            await this.props.record.load();
            this.notification.add("Meal package removed!", { type: "info" });
        } catch (error) {
            this.notification.add("Error removing meal package", { type: "danger" });
        }
    }

    async filterByMeatType(meatType) {
        if (!this.props.record?.resId) return;
        try {
            this.state.meatFilter = meatType;
            await this.orm.write("event.booking", [this.props.record.resId], {
                meat_type_filter: meatType
            });
            await this.props.record.load();
        } catch (error) {
            this.notification.add("Error filtering meals", { type: "danger" });
        }
    }

    calculateTotalCost() {
        const dishes = this.props.record?.data?.selected_dishes || [];
        const meals = this.props.record?.data?.selected_meal_packages || [];
        return dishes.reduce((sum, dish) => sum + (dish.price || 0), 0) + 
               meals.reduce((sum, meal) => sum + (meal.total_meal_price || 0), 0);
    }
}

registry.category("fields").add("meal_selection", {
    component: MealSelectionWidget,
});
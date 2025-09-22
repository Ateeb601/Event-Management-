/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

export class BookingFormController extends FormController {
    setup() {
        super.setup();
        this.notification = useService("notification");
        this.orm = useService("orm");
    }

    async onMeatTypeChange(meatType) {
        if (this.model.root.resId) {
            try {
                await this.orm.write("event.booking", [this.model.root.resId], {
                    meat_type_filter: meatType
                });
                await this.model.root.load();
                this.notification.add(`Filtered to ${meatType} packages`, { type: "success" });
            } catch (error) {
                this.notification.add("Error updating meat filter", { type: "danger" });
            }
        }
    }

    async onPersonCountChange() {
        const totalPerson = this.model.root.data?.total_person;
        if (totalPerson && this.model.root.resId) {
            try {
                const result = await this.orm.searchRead("event.hall", 
                    [["capacity", ">=", totalPerson]],
                    ["id", "name", "capacity"],
                    { order: "capacity asc", limit: 1 }
                );
                
                if (result.length > 0) {
                    await this.orm.write("event.booking", [this.model.root.resId], {
                        hall_id: result[0].id
                    });
                    await this.model.root.load();
                    this.notification.add(`Suggested hall: ${result[0].name}`, { type: "info" });
                }
            } catch (error) {
                this.notification.add("Error updating hall suggestion", { type: "danger" });
            }
        }
    }

    async validateBooking() {
        const data = this.model.root.data;
        if (!data?.start_time || !data?.end_time) {
            this.notification.add("Start and end times are required", { type: "danger" });
            return false;
        }
        if (new Date(data.start_time) >= new Date(data.end_time)) {
            this.notification.add("End time must be after start time", { type: "danger" });
            return false;
        }
        return true;
    }

    async onConfirmBooking() {
        if (await this.validateBooking()) {
            try {
                await this.orm.call("event.booking", "action_confirm", [this.model.root.resId]);
                await this.model.root.load();
                this.notification.add("Booking confirmed successfully!", { type: "success" });
            } catch (error) {
                this.notification.add("Error confirming booking", { type: "danger" });
            }
        }
    }
}

registry.category("views").add("booking_form", {
    ...registry.category("views").get("form"),
    Controller: BookingFormController,
});
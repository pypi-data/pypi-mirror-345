
import { Component, Input, OnInit } from "@angular/core";
import { takeUntil } from "rxjs/operators";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { EventDbController } from "../../controllers/event-db.controller";
import { FilterI } from "../../controllers/event-db.types";

@Component({
    selector: "plugin-eventdb-event-toolbar",
    templateUrl: "event-toolbar.component.html",
    styleUrls: ["./event-toolbar.component.scss"],
})
export class EventDBToolbarComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input() controller: EventDbController;

    colorsEnabled: boolean = false;
    alarmsOnlyEnabled: boolean = false;
    liveEnabled: boolean = true;
    private currentFilter: FilterI | null = null;

    constructor() {
        super();
    }

    override ngOnInit() {
        this.controller
            .getState$()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((state) => {
                this.colorsEnabled = state.colorsEnabled;
                this.alarmsOnlyEnabled = state.alarmsOnlyEnabled;
                this.liveEnabled = state.liveEnabled;
                // Update current filter
                this.currentFilter = {
                    modelSetKey: state.modelSetKey,
                    alarmsOnly: state.alarmsOnlyEnabled,
                    dateTimeRange: state.dateTimeRange,
                    criteria: state.selectedCriterias
                };
            });
    }

    handleDownload(): string {
        let state$ = this.controller.getState$();
        let columnPropKeys: string[] = [];
        let downloadUrl = '';

        state$.pipe(takeUntil(this.onDestroyEvent))
            .subscribe(state => {
                columnPropKeys = state.displayProps.map(prop => prop.key);
                
                if (!this.currentFilter) return;

                downloadUrl = "/peek_plugin_eventdb/download/events?tupleSelector=" +
                    encodeURIComponent(JSON.stringify({
                        modelSetKey: state.modelSetKey,
                        dateTimeRange: this.currentFilter.dateTimeRange,
                        criteria: this.currentFilter.criteria,
                        alarmsOnly: this.currentFilter.alarmsOnly,
                        columnPropKeys: columnPropKeys
                    }));
            });

        return downloadUrl;
    }

    handleColorsToggle(enabled: boolean): void {
        this.controller.updateColors(enabled);
        this.controller.updateRoute();
    }

    handleAlarmsOnlyToggle(enabled: boolean): void {
        this.controller.updateAlarmsOnly(enabled);
        this.controller.updateRoute();
    }

    handleLiveToggle(enabled: boolean): void {
        this.controller.updateLive(enabled);
        this.controller.updateRoute();
    }
}
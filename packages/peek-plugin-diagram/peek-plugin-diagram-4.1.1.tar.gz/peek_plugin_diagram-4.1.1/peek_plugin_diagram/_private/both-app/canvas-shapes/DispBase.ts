import {
    DispLayer,
    DispLevel,
} from "@peek/peek_plugin_diagram/_private/lookups";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { deepCopy } from "@synerty/vortexjs";
import { rotatePointAboutCenter } from "./DispUtil";
import {
    DispActionEnum,
    DispBasePartial,
    DispBaseT,
    DispHandleI,
    DispType,
    PointI,
} from "./DispBasePartial";

export {
    DispBaseT,
    PointI,
    DispHandleTypeE,
    DispHandleI,
    DispType,
    DispActionEnum,
    DispActionPositionOnDataT,
    PointsT,
} from "./DispBasePartial";

export abstract class DispBase extends DispBasePartial {
    private static _typeMapInit = false;
    private static _typeMap = {};

    // Lazy instantiation, because the string types are defined elsewhere
    private static get typeMap() {
        if (!DispBase._typeMapInit) {
            DispBase._typeMapInit = true;
            DispBase._typeMap[DispBase.TYPE_DT] = [DispType.text, "Text"];
            DispBase._typeMap[DispBase.TYPE_DCT] = [
                DispType.curvedText,
                "CurvedText",
            ];
            DispBase._typeMap[DispBase.TYPE_DPG] = [
                DispType.polygon,
                "Polygon",
            ];
            DispBase._typeMap[DispBase.TYPE_DPL] = [
                DispType.polyline,
                "Polyline",
            ];
            DispBase._typeMap[DispBase.TYPE_DE] = [DispType.ellipse, "Ellipse"];
            DispBase._typeMap[DispBase.TYPE_DG] = [DispType.group, "Group"];
            DispBase._typeMap[DispBase.TYPE_DGP] = [
                DispType.groupPointer,
                "GroupPointer",
            ];
            DispBase._typeMap[DispBase.TYPE_DET] = [
                DispType.edgeTemplate,
                "EdgeTemplate",
            ];
            DispBase._typeMap[DispBase.TYPE_DN] = [
                DispType.null_,
                "Deleted Shape",
            ];
        }

        return DispBase._typeMap;
    }

    // Helper query methods

    static typeOf(disp): DispType {
        return DispBase.typeMap[disp._tt][0];
    }

    static resetMoveData(disp): void {
        // Nothing in DispBase to reset
    }

    static hasColor(disp: any) {
        return !!(disp.lcl || disp.fcl || disp.cl);
    }

    static niceName(disp): string {
        return DispBase.typeMap[disp._tt][1];
    }

    // Getters and setters

    static type(disp: DispBaseT): string {
        return disp._tt;
    }

    static geom(disp: DispBaseT): number[] {
        return disp.g || []; // defaults to 0
    }

    static isOverlay(disp: DispBaseT): boolean {
        return disp.o;
    }

    static isSelectable(disp: DispBaseT): boolean {
        return disp.s;
    }

    static setSelectable(disp: DispBaseT, val: boolean): void {
        disp.s = val;
    }

    static key(disp: DispBaseT): string | null {
        return disp.k;
    }

    static setKey(disp: DispBaseT, val: string | null): void {
        disp.k = val;
    }

    static action(disp: DispBaseT): DispActionEnum | null {
        return disp.a;
    }

    static setAction(disp: DispBaseT, val: DispActionEnum | null): void {
        disp.a = val;
    }

    static data(disp: DispBaseT): {} {
        if (disp.d == null) return {};
        return JSON.parse(disp.d);
    }

    static setData(disp: DispBaseT, val: {} | null): void {
        if (val == null) disp.d = null;
        else disp.d = JSON.stringify(val);
    }

    static setBoundsNull(disp: DispBaseT): void {
        disp.bounds = null;

        if (disp.dispGroup != null) {
            DispBase.setBoundsNull(disp.dispGroup);
        }
    }

    // ---------------
    // Delta move helpers

    static deltaMove(disp, dx: number, dy: number) {
        if (disp.g == null) return;

        for (let i = 0; i < disp.g.length; i += 2) {
            disp.g[i] = disp.g[i] + dx;
            disp.g[i + 1] = disp.g[i + 1] + dy;
        }
        DispBase.setBoundsNull(disp);
    }

    static deltaMoveHandle(handle: DispHandleI, dx: number, dy: number) {
        const disp = <DispBaseT>handle.disp;
        if (disp.g == null) return;

        let pointIndex = handle.handleIndex * 2;
        disp.g[pointIndex] = disp.g[pointIndex] + dx;
        disp.g[pointIndex + 1] = disp.g[pointIndex + 1] + dy;
        DispBase.setBoundsNull(disp);
    }

    static rotateAboutAxis(disp, center: PointI, rotationDegrees: number) {
        if (disp.g == null) return;

        for (let i = 0; i < disp.g.length; i += 2) {
            let point = { x: disp.g[i], y: disp.g[i + 1] };
            point = rotatePointAboutCenter(center, point, rotationDegrees);
            disp.g[i] = point.x;
            disp.g[i + 1] = point.y;
        }

        DispBase.setBoundsNull(disp);
    }

    // ---------------
    // Primary Edit Action Handle Point

    static primaryActionHandlePoint(disp, margin: number): PointI | null {
        console.log(
            `ERROR: primaryActionHandlePoint not implemented for ${DispBase.typeOf(
                disp
            )}`
        );
        return null;
    }

    // ---------------
    // Create Handles

    static handlePoints(disp, margin: number): DispHandleI[] {
        console.log(
            `ERROR: Handles not implemented for ${DispBase.typeOf(disp)}`
        );
        return [];
    }

    // ---------------
    // Create Method

    static create(coordSet: ModelCoordSet, type): any {
        let newDisp: any = {
            _tt: type,
        };
        let level = new DispLevel();
        level.id = coordSet.editDefaultLevelId;

        let layer = new DispLayer();
        layer.id = coordSet.editDefaultLayerId;

        DispBase.setLayer(newDisp, layer);
        DispBase.setLevel(newDisp, level);
        DispBase.setSelectable(newDisp, true);
        DispBase.setKey(newDisp, null);
        DispBase.setData(newDisp, null);

        return newDisp;
    }

    // ---------------
    // Populate shape edit context

    static makeShapeContext(context: PeekCanvasShapePropsContext): void {
        context.addProp(
            new ShapeProp(
                ShapePropType.Layer,
                DispBase.layer,
                DispBase.setLayer,
                "Layer"
            )
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Level,
                DispBase.level,
                DispBase.setLevel,
                "Level"
            )
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.String,
                DispBase.key,
                DispBase.setKey,
                "Key"
            )
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Boolean,
                DispBase.isSelectable,
                DispBase.setSelectable,
                "Selectable"
            )
        );
    }

    // ---------------
    // Represent the disp as a user friendly string

    static makeShapeStr(disp: DispBaseT): string {
        return `Type : ${DispBase.niceName(disp)}`;
    }
}

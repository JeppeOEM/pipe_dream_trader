import { StrategyIndicator } from "@/interfaces/StrategyIndicator";
import { create } from "zustand";
import { putStrategyIndicatorsApi, postStrategyIndicatorsApi, deleteStrategyIndicatorsApi } from "../apiClientInstances";

interface StrategyIndicatorStore {
	indicators: StrategyIndicator[];
	indicatorId: number;
	setStrategyIndicators: (indicators: StrategyIndicator[]) => void;
	setStrategyIndicatorId: (id: number) => void;
	addStrategyIndicator: (strategyId: number, indicatorId: number, settings: Record<string, any>) => Promise<void>;
	deleteStrategyIndicator: (id: number) => Promise<void>;
	putStrategyIndicator: (strategyId: number, updatedStrategyIndicator: StrategyIndicator) => Promise<void>;
	getById: () => StrategyIndicator | null;
}

const useStrategyIndicatorStore = create<StrategyIndicatorStore>((set, get) => ({
	indicators: [],
	indicatorId: 0,

	setStrategyIndicators: (indicators: StrategyIndicator[]) => set(() => ({ indicators })),

	setStrategyIndicatorId: (id: number) => set(() => ({ indicatorId: id })),

	addStrategyIndicator: async (strategyId, indicatorId, settings) => {
		try {
			const savedStrategyIndicator = await postStrategyIndicatorsApi.post(strategyId, indicatorId, settings);
			set((state) => ({ indicators: [...state.indicators, savedStrategyIndicator.data] }));
		} catch (error) {
			console.error("Error adding indicator:", error);
		}
	},

	deleteStrategyIndicator: async (id: number) => {
		try {
			await deleteStrategyIndicatorsApi.delete(id);
			set((state) => ({
				indicators: state.indicators.filter((indicator) => indicator.id !== id),
			}));
		} catch (error) {
			console.error("Error deleting indicator:", error);
		}
	},

	putStrategyIndicator: async (strategyId, updatedStrategyIndicator: StrategyIndicator) => {
		try {
			const response = await putStrategyIndicatorsApi.put(
				strategyId,
				updatedStrategyIndicator.id,
				updatedStrategyIndicator
			);
			set((state) => ({
				indicators: state.indicators.map((indicator) =>
					indicator.id === updatedStrategyIndicator.id ? response : indicator
				),
			}));
		} catch (error) {
			console.error("Error updating indicator:", error);
		}
	},

	getById: () => {
		const { indicators, indicatorId } = get();
		const foundStrategyIndicator = indicators.find((indicator) => indicator.id === indicatorId);
		return foundStrategyIndicator || null;
	},
}));

export default useStrategyIndicatorStore;

import { Side, LogicalOperator, CreateConditionRequest } from "@/interfaces/Condition"
import CreateIndicatorIndicatorModal from "./indicator-indicator-modal"
import CreateIndicatorValueModal from "./indicator-value-modal"
import { Button } from "@/components/ui/buttons/button"
interface CreateConditionsProps {
  addCondition: (cond: LogicalOperator | CreateConditionRequest) => void
  side: Side
}

export default function CreateConditions({ side, addCondition }: CreateConditionsProps) {


  function createOperator(side: Side, operator: LogicalOperator) {
    const cond: CreateConditionRequest = {
      "side": side,
      "settings": { "singleOperator": operator }
    }
    return cond
  }
  return (
    <>
      <div className="mt-4 space-x-2 flex flex-row mb-2 p-2 w-full">
        <CreateIndicatorIndicatorModal side={side} addCondition={addCondition} />
        <CreateIndicatorValueModal side={side} addCondition={addCondition} />
        <Button onClick={() => addCondition(createOperator(side, "&"))}>Operator</Button>
      </div>
    </>
  );
}



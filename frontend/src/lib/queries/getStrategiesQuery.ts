
import { useQuery } from "@tanstack/react-query"

import Strategy from "../../interfaces/Strategy"
import { getAllStrategiesApi } from "../apiClientInstances"

const getStrategiesQuery = () => {
  const fetchStrategies = async (): Promise<Strategy[]> => {
    try {
      const strategies: Strategy[] = await getAllStrategiesApi.getAll()
      return strategies
    } catch (error) {
      console.log(error)
      throw new Error("Failed to fetch strategies")
    }
  }

  const { data, error, isError, isLoading } = useQuery<Strategy[], Error>({
    queryKey: ["strategyList"],
    queryFn: fetchStrategies,
  })

  return { data, error, isError, isLoading }
}

export default getStrategiesQuery

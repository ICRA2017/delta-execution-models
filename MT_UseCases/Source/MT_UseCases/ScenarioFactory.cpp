/**
 * Copyright 2017 by Alex Mitrevski <aleksandar.mitrevski@h-brs.de>
 *
 * This file is part of delta-execution-models.
 *
 * delta-execution-models is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * delta-execution-models is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with delta-execution-models. If not, see <http://www.gnu.org/licenses/>.
 */

#include "MT_UseCases.h"
#include "ScenarioFactory.h"

ScenarioPtr ScenarioFactory::LoadScenario(ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies)
{
	if (scenarioConfig.type == ScenarioTypes::CONTAINER)
	{
		return new ContainerScenario(scenarioConfig, displayConfig, copies);
	}
	else if (scenarioConfig.type == ScenarioTypes::CUBE_TOWER)
	{
		return new CubeTowerScenario(scenarioConfig, displayConfig, copies);
	}
	else if (scenarioConfig.type == ScenarioTypes::FRIDGE)
	{
		return new FridgeScenario(scenarioConfig, displayConfig, copies);
	}
	else if (scenarioConfig.type == ScenarioTypes::TABLE)
	{
		return new TableScenario(scenarioConfig, displayConfig, copies);
	}

	return NULL;
}

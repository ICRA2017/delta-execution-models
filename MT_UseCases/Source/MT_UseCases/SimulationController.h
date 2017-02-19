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

#pragma once

#include "Structs.h"
#include "Scenario.h"
#include "ScenarioConfigParser.h"
#include "ScenarioFactory.h"

#include "external/tinyxml2.h"

#include "GameFramework/Actor.h"
#include "SimulationController.generated.h"

UCLASS()
class MT_USECASES_API ASimulationController : public AActor
{
	GENERATED_BODY()

public:
	ASimulationController(const FObjectInitializer& objectInitialiser);
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FString parametersFile;

protected:
	ScenarioPtr scenario;

	ScenarioConfig scenarioConfig;
	DisplayConfig displayConfig;
	int scenarioCopies;
	float duration;
	float maxLoopDuration;
	Tolerances tolerances;
	string logFile;
    bool simulationOver;
};

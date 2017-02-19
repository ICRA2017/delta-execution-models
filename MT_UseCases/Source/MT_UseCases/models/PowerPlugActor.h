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

#include "GameFramework/Actor.h"
#include "SimulationActor.h"
#include "PowerPlugActor.generated.h"

UCLASS()
class MT_USECASES_API APowerPlugActor : public ASimulationActor
{
	GENERATED_BODY()

public:
	APowerPlugActor(const FObjectInitializer& objectInitialiser);
	virtual void BeginPlay() override;
	virtual void Tick( float DeltaSeconds ) override;
};

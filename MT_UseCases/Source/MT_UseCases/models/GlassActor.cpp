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
#include "GlassActor.h"

AGlassActor::AGlassActor(const FObjectInitializer& objectInitialiser)
	: Super(objectInitialiser, TEXT("/Game/objects/glass.glass"))
{
	PrimaryActorTick.bCanEverTick = true;

	MeshParams meshParams(TEXT("Glass"), FVector(0.212121, 0.212121, 0.263157), true, true, 4.07f, FVector(0, 0, 5));  //mass = 600g, size=(7,7,10)cm
	this->AddMesh(objectInitialiser, meshParams);
}

void AGlassActor::BeginPlay()
{
	Super::BeginPlay();
}

void AGlassActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

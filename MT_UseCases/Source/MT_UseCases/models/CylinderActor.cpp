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
#include "CylinderActor.h"

ACylinderActor::ACylinderActor(const FObjectInitializer& objectInitialiser)
	: Super(objectInitialiser, TEXT("/Game/objects/cylinder.cylinder"))
{
	PrimaryActorTick.bCanEverTick = true;

	MeshParams meshParams(TEXT("Cylinder"), FVector(0.307692, 0.307692, 0.653846), true, true, 0.0755f, FVector(0, 0, 12.75)); //mass = 100g, size=(8, 8, 25.5)cm
	this->AddMesh(objectInitialiser, meshParams);
}

void ACylinderActor::BeginPlay()
{
	Super::BeginPlay();
}

void ACylinderActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

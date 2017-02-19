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
#include "SimulationActor.h"

ASimulationActor::ASimulationActor()
	: Super()
{
	PrimaryActorTick.bCanEverTick = true;
	this->mesh = nullptr;
}

ASimulationActor::ASimulationActor(const FObjectInitializer& objectInitialiser, const TCHAR* meshReference)
	: Super(objectInitialiser)
{
	PrimaryActorTick.bCanEverTick = true;
	this->mesh = new ConstructorHelpers::FObjectFinder<UStaticMesh>(meshReference);
}

void ASimulationActor::BeginPlay()
{
	Super::BeginPlay();
}

void ASimulationActor::Tick( float DeltaTime )
{
	Super::Tick( DeltaTime );
}

void ASimulationActor::AddMesh(const FObjectInitializer& objectInitialiser, MeshParams meshParams)
{
	this->objectMesh = this->mesh->Object;
	this->meshSubobject = objectInitialiser.CreateDefaultSubobject<UStaticMeshComponent>(this, meshParams.text);
	this->meshSubobject->AttachTo(this->RootComponent);
	this->meshSubobject->SetStaticMesh(this->objectMesh);
	this->meshSubobject->bCastDynamicShadow = true;
	this->meshSubobject->CastShadow = true;
	this->meshSubobject->SetSimulatePhysics(meshParams.enablePhysics);
	this->meshSubobject->SetEnableGravity(meshParams.enableGravity);
	this->meshSubobject->bGenerateOverlapEvents = true;
	this->meshSubobject->AttachSocketName = meshParams.text;
	this->meshSubobject->SetRelativeScale3D(meshParams.scale);

	this->RootComponent = this->meshSubobject;

	if (!GEngine) return;
	FBodyInstance* body = this->meshSubobject->GetBodyInstance();
	if (!body) return;
	body->SetMassScale(meshParams.massScale);
	body->COMNudge += meshParams.comOffset;
}

Pose ASimulationActor::GetPose()
{
	Pose pose;
	pose.pos = this->meshSubobject->GetComponentLocation();
	pose.rot = this->meshSubobject->GetComponentRotation();
	return pose;
}

void ASimulationActor::SetScale(FVector scale)
{
	this->SetActorScale3D(scale);
}

float ASimulationActor::GetMass()
{
	return this->meshSubobject->GetMass();
}

void ASimulationActor::SetMassScale(float scale)
{
	FBodyInstance* body = this->meshSubobject->GetBodyInstance();
	body->SetMassScale(scale);
}

void ASimulationActor::SetCOMOffset(FVector offset)
{
	FBodyInstance* body = this->meshSubobject->GetBodyInstance();
	body->COMNudge += offset;
}

void ASimulationActor::SetLocation(FVector position)
{
	this->meshSubobject->SetWorldLocation(position);
}

void ASimulationActor::SetRotation(FRotator orientation)
{
	this->meshSubobject->SetWorldRotation(orientation);
}

void ASimulationActor::SetPose(Pose pose)
{
	this->SetPose(pose.pos, pose.rot);
}

void ASimulationActor::SetPose(FVector position, FRotator orientation)
{
	this->meshSubobject->SetWorldLocation(position);
	this->meshSubobject->SetWorldRotation(orientation);
}

void ASimulationActor::ApplyForce(FVector force)
{
	this->meshSubobject->AddForce(force);
}

void ASimulationActor::SetPhysics(bool toggle)
{
	this->meshSubobject->SetSimulatePhysics(toggle);
}

void ASimulationActor::EnablePhysics()
{
	this->meshSubobject->SetSimulatePhysics(true);
}

void ASimulationActor::DisablePhysics()
{
	this->meshSubobject->SetSimulatePhysics(false);
}

void ASimulationActor::EnableGravity()
{
	this->meshSubobject->SetEnableGravity(true);
}

void ASimulationActor::DisableGravity()
{
	this->meshSubobject->SetEnableGravity(false);
}

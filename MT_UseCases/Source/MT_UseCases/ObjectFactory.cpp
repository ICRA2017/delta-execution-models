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
#include "ObjectFactory.h"

ASimulationActor* ObjectFactory::GetObject(string objectType)
{
	if (objectType == ObjectTypes::FLOOR)
	{
		return (AFloorActor*)GWorld->SpawnActor(AFloorActor::StaticClass());
	}
	else if (objectType == ObjectTypes::BOOKSHELF)
	{
		return (ABookcaseActor*)GWorld->SpawnActor(ABookcaseActor::StaticClass());
	}
	else if (objectType == ObjectTypes::FRIDGE)
	{
		return (AFridgeActor*)GWorld->SpawnActor(AFridgeActor::StaticClass());
	}
	else if (objectType == ObjectTypes::BOOK)
	{
		return (ABookActor*)GWorld->SpawnActor(ABookActor::StaticClass());
	}
	else if (objectType == ObjectTypes::BOTTLE)
	{
		return (AKetchupBottleActor*)GWorld->SpawnActor(AKetchupBottleActor::StaticClass());
	}
	else if (objectType == ObjectTypes::CUP)
	{
		return (ACupActor*)GWorld->SpawnActor(ACupActor::StaticClass());
	}
	else if (objectType == ObjectTypes::GLASS)
	{
		return (AGlassActor*)GWorld->SpawnActor(AGlassActor::StaticClass());
	}
	else if (objectType == ObjectTypes::CYLINDER)
	{
		return (ACylinderActor*)GWorld->SpawnActor(ACylinderActor::StaticClass());
	}
	else if (objectType == ObjectTypes::CUBE)
	{
		return (ACubeActor*)GWorld->SpawnActor(ACubeActor::StaticClass());
	}

	return (ASimulationActor*)GWorld->SpawnActor(ASimulationActor::StaticClass());
}

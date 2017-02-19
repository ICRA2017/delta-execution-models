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
#include "CubeTowerScenario.h"

CubeTowerScenario::CubeTowerScenario(ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies)
	: Scenario(scenarioConfig, displayConfig, copies)
{ }

void CubeTowerScenario::SaveLearningData(const string& file, const Tolerances& tolerances) const
{
	string data = "";
	for (unsigned int i = 0; i<this->objects.size(); i++)
	{
		Objects objects;
		objects.manipObj = this->objects[i][1];
		objects.staticObj.push_back(this->objects[i][2]);
        objects.staticObjIdx.push_back(2);

		this->GetDeltaNotData(objects, data, i);
		bool success = this->IsSuccessful(objects, i, tolerances);

		if (success)
			data += "1";
		else
			data += "0";
		data += "\n";
	}

	std::ofstream fileStream;
	fileStream.open(file, std::ios::app);
	fileStream << data;
	fileStream.close();
}

bool CubeTowerScenario::IsSuccessful(const Objects& objects, int idx, const Tolerances& tolerances) const
{
	FVector initStaticPos = this->initPositions[idx][objects.staticObjIdx[0]];
	FRotator initStaticRot = this->initRotations[idx][objects.staticObjIdx[0]];

	const FBox& finalManipBox = objects.manipObj->GetComponentsBoundingBox(false);

	Pose finalStaticPose = objects.staticObj[0]->GetPose();
	const FBox& finalStaticBox = objects.staticObj[0]->GetComponentsBoundingBox(false);

	bool movingOnStatic = abs(finalManipBox.Min.Z - finalStaticBox.Max.Z) < tolerances.translationEpsilon;
	bool staticSamePose = IsPoseSame(Pose(initStaticPos, initStaticRot), finalStaticPose, tolerances.translationTolerance);

	return (movingOnStatic && staticSamePose);
}

void CubeTowerScenario::UpdateTrials(TrialData& trialData, const Tolerances& tolerances)
{
	for (unsigned int i = 0; i<this->objects.size(); i++)
	{
		if (trialData.copyToTrialMap[i] >= trialData.numberOfTrials)
			continue;

		Objects objects;
		if (this->manipulatedObjectIdx[i] == 0)
        {
			objects.staticObj.push_back(this->objects[i][this->manipulatedObjects[i].size() + 1]);
            objects.staticObjIdx.push_back(this->manipulatedObjects[i].size() + 1);
        }
		else
        {
			objects.staticObj.push_back(this->objects[i][this->manipulatedObjectIdx[i] - 1]);
            objects.staticObjIdx.push_back(this->manipulatedObjectIdx[i] - 1);
        }
		objects.manipObj = this->objects[i][this->manipulatedObjectIdx[i]];

		bool partialSuccess = this->IsSuccessful(objects, i, tolerances);
		bool success = false;
		if (partialSuccess && this->manipulatedObjectIdx[i] == this->manipulatedObjects[i].size())
			success = true;

		if (success)
		{
			string message = "Trial " + std::to_string(trialData.copyToTrialMap[i]) + " finished with success";
			GEngine->AddOnScreenDebugMessage(-1, 2, FColor(255, 0, 0), FString(message.c_str()));
			trialData.trialSuccess[trialData.copyToTrialMap[i]] = true;
			trialData.trialCompleted[trialData.copyToTrialMap[i]] = true;
			trialData.copyToTrialMap[i] = trialData.trialCounter;
			trialData.trialCounter += 1;
			this->manipulatedObjectIdx[i] = 0;
		}
		else
		{
			if (!partialSuccess)
			{
				if (this->manipulatedObjectIdx[i] > 1)
				{
					Pose initStaticPose = Pose(this->initPositions[i][this->manipulatedObjectIdx[i] - 1], this->initRotations[i][this->manipulatedObjectIdx[i] - 1]);
					Pose finalStaticPose = this->objects[i][this->manipulatedObjectIdx[i] - 1]->GetPose();

					if (!IsPoseSame(initStaticPose, finalStaticPose, tolerances.translationTolerance))
					{
						this->manipulatedObjectIdx[i] = 1;
					}
				}

				if (trialData.attemptCounters[trialData.copyToTrialMap[i]] < trialData.attemptsPerTrial)
				{
					trialData.attemptCounters[trialData.copyToTrialMap[i]] += 1;
				}
				else
				{
					string message = "Trial " + std::to_string(trialData.copyToTrialMap[i]) + " finished with failure";
					GEngine->AddOnScreenDebugMessage(-1, 2, FColor(255, 0, 0), FString(message.c_str()));
					trialData.trialCompleted[trialData.copyToTrialMap[i]] = true;
					trialData.copyToTrialMap[i] = trialData.trialCounter;
					trialData.trialCounter += 1;
				}
			}
			else
			{
				Pose pose = this->objects[i][this->manipulatedObjectIdx[i]]->GetPose();
				this->initPositions[i][this->manipulatedObjectIdx[i]] = pose.pos;
				this->initRotations[i][this->manipulatedObjectIdx[i]] = pose.rot;
				this->initBoundingBoxes[i][this->manipulatedObjectIdx[i]] = this->objects[i][this->manipulatedObjectIdx[i]]->GetComponentsBoundingBox(false);
				this->manipulatedObjectIdx[i] += 1;
			}
		}
	}
}

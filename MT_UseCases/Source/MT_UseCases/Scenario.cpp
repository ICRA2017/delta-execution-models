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
#include "Scenario.h"

Scenario::Scenario(ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies)
{
	this->copyCount = copies;

	if (scenarioConfig.simulationType == SimulationTypes::OPTIMISED && scenarioConfig.trialData.numberOfTrials > 0)
	{
		this->InitialiseTrials(scenarioConfig, copies);
	}

	this->CreateScenario(scenarioConfig, displayConfig, copies);
}

void Scenario::InitialiseTrials(ScenarioConfig& scenarioConfig, int copies)
{
	scenarioConfig.trialData.trialCounter = 0;
	for (int i = 0; i < scenarioConfig.trialData.numberOfTrials; i++)
	{
		scenarioConfig.trialData.trialSuccess.push_back(false);
		scenarioConfig.trialData.trialCompleted.push_back(false);
		scenarioConfig.trialData.attemptCounters.push_back(1);
	}

	for (int i = 0; i < copies; i++)
	{
		scenarioConfig.trialData.copyToTrialMap.insert(std::pair<int, int>(i, scenarioConfig.trialData.trialCounter));
		scenarioConfig.trialData.trialCounter += 1;
	}
}

void Scenario::CreateScenario(const ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies)
{
	int numberOfFloors = (copies - 1) / displayConfig.copiesPerFloor + 1;
	for (int i = 0; i < numberOfFloors; i++)
	{
		this->floors.push_back(ObjectFactory::GetObject(ObjectTypes::FLOOR));
		this->floors[i]->SetPose(FVector(i * displayConfig.floorOffset, 0, 0), FRotator(0, 0, 0));
	}

	this->poseGenerator.InitDistributions(scenarioConfig.posMin, scenarioConfig.posMax, scenarioConfig.rotMin, scenarioConfig.rotMax);
	for (int i = 0; i<copies; i++)
	{
		int row = i % displayConfig.displayRows;
		int column = i / displayConfig.displayRows;
		this->objects.push_back(vector<ASimulationActor*>());
		this->manipulatedObjects.push_back(vector<ASimulationActor*>());
		this->manipulatedObjectIdx.push_back(1);
		this->initPositions.push_back(vector<FVector>());
		this->initRotations.push_back(vector<FRotator>());
		this->initBoundingBoxes.push_back(vector<FBox>());
		this->poseCache.push_back(vector<Pose>());
        this->poseCacheIdx.push_back(0);

		for (int j = 0; j<scenarioConfig.models.size(); j++)
		{
			this->AddModel(i, scenarioConfig.models[j], displayConfig, row, column);
		}

		if (scenarioConfig.simulationType == SimulationTypes::RANDOM)
		{
			bool intersectingObjects = true;
			FBox box;
			while (intersectingObjects)
			{
				this->SetManipulatedObjectPose(i, scenarioConfig, displayConfig, row, column);
				box = this->objects[i][this->manipulatedObjectIdx[i]]->GetComponentsBoundingBox(false);
				for (int j = 1; j < scenarioConfig.models.size(); j++)
				{
					if (j == (this->manipulatedObjectIdx[i]))
						continue;

					intersectingObjects = box.Intersect(this->objects[i][j]->GetComponentsBoundingBox(false));
					if (intersectingObjects)
						break;
				}
			}
		}
		else
		{
			this->SetManipulatedObjectPose(i, scenarioConfig, displayConfig, row, column);
		}
	}
}

void Scenario::UpdateScenario(const ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig)
{
	for (int i = 0; i<this->copyCount; i++)
	{
		int row = i % displayConfig.displayRows;
		int column = i / displayConfig.displayRows;
		for (int j = 0; j<scenarioConfig.models.size(); j++)
		{
			if (j > 0 && j < (this->manipulatedObjectIdx[i]))
				continue;
			else
			{
				double x = scenarioConfig.models[j].position.X + column * displayConfig.columnOffset;
				double y = scenarioConfig.models[j].position.Y + row * displayConfig.rowOffset;
				double z = scenarioConfig.models[j].position.Z;
				double roll = scenarioConfig.models[j].orientation.Roll;
				double pitch = scenarioConfig.models[j].orientation.Pitch;
				double yaw = scenarioConfig.models[j].orientation.Yaw;

				Pose pose(x, y, z, roll, pitch, yaw);
				this->objects[i][j]->SetPose(pose);
			}
		}

		if (scenarioConfig.simulationType == SimulationTypes::RANDOM)
		{
			bool intersectingObjects = true;
			FBox box;
			while (intersectingObjects)
			{
				this->SetManipulatedObjectPose(i, scenarioConfig, displayConfig, row, column);
				box = this->objects[i][this->manipulatedObjectIdx[i]]->GetComponentsBoundingBox(false);
				for (int j = 1; j < scenarioConfig.models.size(); j++)
				{
					if (j == (this->manipulatedObjectIdx[i] + 1))
						continue;

					intersectingObjects = box.Intersect(this->objects[i][j]->GetComponentsBoundingBox(false));
					if (intersectingObjects)
						break;
				}
			}
		}
		else
		{
			this->SetManipulatedObjectPose(i, scenarioConfig, displayConfig, row, column);
		}
	}
}

void Scenario::AddModel(int copyIdx, const ModelConfig& modelConfig, const DisplayConfig& displayConfig, int row, int column)
{
	this->objects[copyIdx].push_back(ObjectFactory::GetObject(modelConfig.type));
	int objectIdx = this->objects[copyIdx].size() - 1;
	if (modelConfig.name.find("manipulated") != std::string::npos)
	{
		this->manipulatedObjects[copyIdx].push_back(this->objects[copyIdx][objectIdx]);
	}

	double x = modelConfig.position.X + column * displayConfig.columnOffset;
	double y = modelConfig.position.Y + row * displayConfig.rowOffset;
	double z = modelConfig.position.Z;
	double roll = modelConfig.orientation.Roll;
	double pitch = modelConfig.orientation.Pitch;
	double yaw = modelConfig.orientation.Yaw;

	if (modelConfig.scale[0] > 0.0f)
    {
		this->objects[copyIdx][objectIdx]->SetScale(FVector(modelConfig.scale[0], modelConfig.scale[1], modelConfig.scale[2]));
    }
	this->objects[copyIdx][objectIdx]->SetCOMOffset(FVector(modelConfig.comOffset[0], modelConfig.comOffset[1], modelConfig.comOffset[2]));
	this->objects[copyIdx][objectIdx]->SetMassScale(modelConfig.massScale);
	this->objects[copyIdx][objectIdx]->SetPose(FVector(x, y, z), FRotator(pitch, yaw, roll));
	this->objects[copyIdx][objectIdx]->SetPhysics(modelConfig.simulatePhysics);

	this->initPositions[copyIdx].push_back(FVector(x, y, z));
	this->initRotations[copyIdx].push_back(FRotator(pitch, yaw, roll));
	this->initBoundingBoxes[copyIdx].push_back(this->objects[copyIdx][objectIdx]->GetComponentsBoundingBox(false));
}

void Scenario::SetManipulatedObjectPose(int copyIdx, const ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int row, int column)
{
	Pose pose = this->GenerateRandomPose();
	pose.pos.X = pose.pos.X + column * displayConfig.columnOffset;
	pose.pos.Y = pose.pos.Y + row * displayConfig.rowOffset;
	this->objects[copyIdx][this->manipulatedObjectIdx[copyIdx]]->SetPose(pose);

	if (scenarioConfig.simulationType == SimulationTypes::OPTIMISED)
	{
		if (this->poseCacheIdx[copyIdx] == this->poseCache[copyIdx].size())
		{
			this->poseCacheIdx[copyIdx] = 0;
			this->poseCache[copyIdx] = this->GenerateOptimisedPoses(copyIdx, scenarioConfig.optimisationParams);
		}
		pose = this->poseCache[copyIdx][this->poseCacheIdx[copyIdx]];
		this->poseCacheIdx[copyIdx]++;
        this->objects[copyIdx][this->manipulatedObjectIdx[copyIdx]]->SetPose(pose);
	}
	else if (scenarioConfig.simulationType == SimulationTypes::ROTATION_OPTIMISED)
	{
		if (this->poseCacheIdx[copyIdx] == this->poseCache[copyIdx].size())
		{
			this->poseCacheIdx[copyIdx] = 0;
			this->poseCache[copyIdx] = this->GenerateOptimisedPoses(copyIdx, scenarioConfig.optimisationParams);
		}
		pose = this->poseCache[copyIdx][this->poseCacheIdx[copyIdx]];
		this->poseCacheIdx[copyIdx]++;

        this->objects[copyIdx][this->manipulatedObjectIdx[copyIdx]]->SetRotation(pose.rot);
        pose = this->objects[copyIdx][this->manipulatedObjectIdx[copyIdx]]->GetPose();
	}
	else
	{
		this->objects[copyIdx][this->manipulatedObjectIdx[copyIdx]]->SetPose(pose);
	}

	//we save the pose and bounding box of the manipulated object
	this->initPositions[copyIdx][this->manipulatedObjectIdx[copyIdx]] = pose.pos;
	this->initRotations[copyIdx][this->manipulatedObjectIdx[copyIdx]] = pose.rot;
	this->initBoundingBoxes[copyIdx][this->manipulatedObjectIdx[copyIdx]] = this->objects[copyIdx][this->manipulatedObjectIdx[copyIdx]]->GetComponentsBoundingBox(false);
}

void Scenario::GetDeltaData(const Objects& objects, string& data, int idx) const
{
	// we get the initial poses and bounding boxes
	FVector initManipPos = this->initPositions[idx][1];
	FRotator initManipRot = this->initRotations[idx][1];
	const FBox& initManipBox = this->initBoundingBoxes[idx][1];

	FVector initStatic1Pos = this->initPositions[idx][2];
	FRotator initStatic1Rot = this->initRotations[idx][2];
	const FBox& initStatic1Box = this->initBoundingBoxes[idx][2];

	FVector initStatic2Pos = this->initPositions[idx][3];
	FRotator initStatic2Rot = this->initRotations[idx][3];
	const FBox& initStatic2Box = this->initBoundingBoxes[idx][3];

	// we get the final initial and bounding boxes
	Pose finalManipPose = objects.manipObj->GetPose();
	const FBox& finalManipBox = objects.manipObj->GetComponentsBoundingBox(false);

	Pose finalStatic1Pose = objects.staticObj[0]->GetPose();
	const FBox& finalStatic1Box = objects.staticObj[0]->GetComponentsBoundingBox(false);

	Pose finalStatic2Pose = objects.staticObj[1]->GetPose();
	const FBox& finalStatic2Box = objects.staticObj[1]->GetComponentsBoundingBox(false);

	// we prepare the data for saving

	// manipulated object data
	data += to_string(initManipPos.X) + " " + to_string(initManipPos.Y) + " " + to_string(initManipPos.Z) + " ";
	data += to_string(initManipRot.Roll) + " " + to_string(initManipRot.Pitch) + " " + to_string(initManipRot.Yaw) + " ";

	data += to_string(finalManipPose.pos.X) + " " + to_string(finalManipPose.pos.Y) + " " + to_string(finalManipPose.pos.Z) + " ";
	data += to_string(finalManipPose.rot.Roll) + " " + to_string(finalManipPose.rot.Pitch) + " " + to_string(finalManipPose.rot.Yaw) + " ";

	data += to_string(initManipBox.Min.X) + " " + to_string(initManipBox.Min.Y) + " " + to_string(initManipBox.Min.Z) + " ";
	data += to_string(initManipBox.Max.X) + " " + to_string(initManipBox.Max.Y) + " " + to_string(initManipBox.Max.Z) + " ";

	data += to_string(finalManipBox.Min.X) + " " + to_string(finalManipBox.Min.Y) + " " + to_string(finalManipBox.Min.Z) + " ";
	data += to_string(finalManipBox.Max.X) + " " + to_string(finalManipBox.Max.Y) + " " + to_string(finalManipBox.Max.Z) + " ";

	//static 1 data
	data += to_string(initStatic1Pos.X) + " " + to_string(initStatic1Pos.Y) + " " + to_string(initStatic1Pos.Z) + " ";
	data += to_string(initStatic1Rot.Roll) + " " + to_string(initStatic1Rot.Pitch) + " " + to_string(initStatic1Rot.Yaw) + " ";

	data += to_string(finalStatic1Pose.pos.X) + " " + to_string(finalStatic1Pose.pos.Y) + " " + to_string(finalStatic1Pose.pos.Z) + " ";
	data += to_string(finalStatic1Pose.rot.Roll) + " " + to_string(finalStatic1Pose.rot.Pitch) + " " + to_string(finalStatic1Pose.rot.Yaw) + " ";

	data += to_string(initStatic1Box.Min.X) + " " + to_string(initStatic1Box.Min.Y) + " " + to_string(initStatic1Box.Min.Z) + " ";
	data += to_string(initStatic1Box.Max.X) + " " + to_string(initStatic1Box.Max.Y) + " " + to_string(initStatic1Box.Max.Z) + " ";

	data += to_string(finalStatic1Box.Min.X) + " " + to_string(finalStatic1Box.Min.Y) + " " + to_string(finalStatic1Box.Min.Z) + " ";
	data += to_string(finalStatic1Box.Max.X) + " " + to_string(finalStatic1Box.Max.Y) + " " + to_string(finalStatic1Box.Max.Z) + " ";

	//static 2 data
	data += to_string(initStatic2Pos.X) + " " + to_string(initStatic2Pos.Y) + " " + to_string(initStatic2Pos.Z) + " ";
	data += to_string(initStatic2Rot.Roll) + " " + to_string(initStatic2Rot.Pitch) + " " + to_string(initStatic2Rot.Yaw) + " ";

	data += to_string(finalStatic2Pose.pos.X) + " " + to_string(finalStatic2Pose.pos.Y) + " " + to_string(finalStatic2Pose.pos.Z) + " ";
	data += to_string(finalStatic2Pose.rot.Roll) + " " + to_string(finalStatic2Pose.rot.Pitch) + " " + to_string(finalStatic2Pose.rot.Yaw) + " ";

	data += to_string(initStatic2Box.Min.X) + " " + to_string(initStatic2Box.Min.Y) + " " + to_string(initStatic2Box.Min.Z) + " ";
	data += to_string(initStatic2Box.Max.X) + " " + to_string(initStatic2Box.Max.Y) + " " + to_string(initStatic2Box.Max.Z) + " ";

	data += to_string(finalStatic2Box.Min.X) + " " + to_string(finalStatic2Box.Min.Y) + " " + to_string(finalStatic2Box.Min.Z) + " ";
	data += to_string(finalStatic2Box.Max.X) + " " + to_string(finalStatic2Box.Max.Y) + " " + to_string(finalStatic2Box.Max.Z) + " ";
}

void Scenario::GetDeltaNotData(const Objects& objects, string& data, int idx) const
{
	// we get the initial poses and bounding boxes
	FVector initManipPos = this->initPositions[idx][1];
	FRotator initManipRot = this->initRotations[idx][1];
	const FBox& initManipBox = this->initBoundingBoxes[idx][1];

	FVector initStaticPos = this->initPositions[idx][2];
	FRotator initStaticRot = this->initRotations[idx][2];
	const FBox& initStaticBox = this->initBoundingBoxes[idx][2];

	// we get the final initial and bounding boxes
	Pose finalManipPose = objects.manipObj->GetPose();
	const FBox& finalManipBox = objects.manipObj->GetComponentsBoundingBox(false);

	Pose finalStaticPose = objects.staticObj[0]->GetPose();
	const FBox& finalStaticBox = objects.staticObj[0]->GetComponentsBoundingBox(false);


	// we prepare the data for saving

	// manipulated object data
	data += to_string(initManipPos.X) + " " + to_string(initManipPos.Y) + " " + to_string(initManipPos.Z) + " ";
	data += to_string(initManipRot.Roll) + " " + to_string(initManipRot.Pitch) + " " + to_string(initManipRot.Yaw) + " ";

	data += to_string(finalManipPose.pos.X) + " " + to_string(finalManipPose.pos.Y) + " " + to_string(finalManipPose.pos.Z) + " ";
	data += to_string(finalManipPose.rot.Roll) + " " + to_string(finalManipPose.rot.Pitch) + " " + to_string(finalManipPose.rot.Yaw) + " ";

	data += to_string(initManipBox.Min.X) + " " + to_string(initManipBox.Min.Y) + " " + to_string(initManipBox.Min.Z) + " ";
	data += to_string(initManipBox.Max.X) + " " + to_string(initManipBox.Max.Y) + " " + to_string(initManipBox.Max.Z) + " ";

	data += to_string(finalManipBox.Min.X) + " " + to_string(finalManipBox.Min.Y) + " " + to_string(finalManipBox.Min.Z) + " ";
	data += to_string(finalManipBox.Max.X) + " " + to_string(finalManipBox.Max.Y) + " " + to_string(finalManipBox.Max.Z) + " ";

	//static data
	data += to_string(initStaticPos.X) + " " + to_string(initStaticPos.Y) + " " + to_string(initStaticPos.Z) + " ";
	data += to_string(initStaticRot.Roll) + " " + to_string(initStaticRot.Pitch) + " " + to_string(initStaticRot.Yaw) + " ";

	data += to_string(finalStaticPose.pos.X) + " " + to_string(finalStaticPose.pos.Y) + " " + to_string(finalStaticPose.pos.Z) + " ";
	data += to_string(finalStaticPose.rot.Roll) + " " + to_string(finalStaticPose.rot.Pitch) + " " + to_string(finalStaticPose.rot.Yaw) + " ";

	data += to_string(initStaticBox.Min.X) + " " + to_string(initStaticBox.Min.Y) + " " + to_string(initStaticBox.Min.Z) + " ";
	data += to_string(initStaticBox.Max.X) + " " + to_string(initStaticBox.Max.Y) + " " + to_string(initStaticBox.Max.Z) + " ";

	data += to_string(finalStaticBox.Min.X) + " " + to_string(finalStaticBox.Min.Y) + " " + to_string(finalStaticBox.Min.Z) + " ";
	data += to_string(finalStaticBox.Max.X) + " " + to_string(finalStaticBox.Max.Y) + " " + to_string(finalStaticBox.Max.Z) + " ";
}

Pose Scenario::GenerateRandomPose()
{
	return this->poseGenerator.GeneratePose();
}

vector<Pose> Scenario::GenerateOptimisedPoses(int copyIdx, const OptimisationParams& optimisationParams)
{
	this->WriteOptimisationData(copyIdx, optimisationParams);
	this->CallOptimisationScript(optimisationParams.optimisationScript);
	vector<Pose> poses = this->ReadOptimisedData(optimisationParams.optimisedDataFile);
	return poses;
}

void Scenario::WriteOptimisationData(int copyIdx, const OptimisationParams& optimisationParams)
{
	string data = "";

	ASimulationActor* manipObj = this->objects[copyIdx][this->manipulatedObjectIdx[copyIdx]];
	Pose manipPose = manipObj->GetPose();
	const FBox& manipBox = manipObj->GetComponentsBoundingBox(false);

	data += to_string(manipPose.pos.X) + "\n" + to_string(manipPose.pos.Y) + "\n" + to_string(manipPose.pos.Z) + "\n";
	data += to_string(manipPose.rot.Roll) + "\n" + to_string(manipPose.rot.Pitch) + "\n" + to_string(manipPose.rot.Yaw) + "\n";
	data += to_string(manipBox.Min.X) + "\n" + to_string(manipBox.Min.Y) + "\n" + to_string(manipBox.Min.Z) + "\n";
	data += to_string(manipBox.Max.X) + "\n" + to_string(manipBox.Max.Y) + "\n" + to_string(manipBox.Max.Z) + "\n";

	for (int i = 1; i<this->objects[copyIdx].size(); i++)
	{
        //in a multi-step scenario, the optimisation shouldn't consider the manipulated objects that are used in the action later
		if (i == (this->manipulatedObjectIdx[copyIdx]) || (i > this->manipulatedObjectIdx[copyIdx] && i < (this->manipulatedObjects[copyIdx].size() + 1)))
			continue;

		ASimulationActor* obj = this->objects[copyIdx][i];
		Pose pose = obj->GetPose();
		const FBox& box = obj->GetComponentsBoundingBox(false);

		data += to_string(pose.pos.X) + "\n" + to_string(pose.pos.Y) + "\n" + to_string(pose.pos.Z) + "\n";
		data += to_string(pose.rot.Roll) + "\n" + to_string(pose.rot.Pitch) + "\n" + to_string(pose.rot.Yaw) + "\n";
		data += to_string(box.Min.X) + "\n" + to_string(box.Min.Y) + "\n" + to_string(box.Min.Z) + "\n";
		data += to_string(box.Max.X) + "\n" + to_string(box.Max.Y) + "\n" + to_string(box.Max.Z) + "\n";
	}

	std::ofstream fileStream;
	fileStream.open(optimisationParams.optimisationDataFile);
	fileStream << data;
	fileStream.close();

	fileStream.open(optimisationParams.keysFile);
	fileStream << optimisationParams.keys;
	fileStream.close();
}

void Scenario::CallOptimisationScript(const string& scriptName)
{
	string optimisationCommand = "python " + scriptName;
	std::wstring commandWideStr = std::wstring(optimisationCommand.begin(), optimisationCommand.end());
	LPTSTR command = _tcsdup(commandWideStr.c_str());

	STARTUPINFO si;
	PROCESS_INFORMATION pi;
	ZeroMemory(&si, sizeof(si));
	si.cb = sizeof(si);
	ZeroMemory(&pi, sizeof(pi));

	if (CreateProcess(NULL, command, NULL, NULL, false, CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
		WaitForSingleObject(pi.hProcess, INFINITE);
}

vector<Pose> Scenario::ReadOptimisedData(const string& file)
{
	std::ifstream fileStream;
	fileStream.open(file);
	string line;

	vector<Pose> poses;
	while (std::getline(fileStream, line))
	{
		if (line.length() == 0)
			continue;

		vector<float> data;
		int prevSubstrStart = 0;
		for (int i = 0; i < line.length(); i++)
		{
			if (line[i] == ' ')
			{
				string substr = line.substr(prevSubstrStart, i - prevSubstrStart);
				prevSubstrStart = i + 1;

				float converted = stof(substr);
				data.push_back(converted);
			}
		}

		string substr = line.substr(prevSubstrStart, line.length() - prevSubstrStart);
		float converted = stof(substr);
		data.push_back(converted);

		poses.push_back(Pose(data[0], data[1], data[2], data[3], data[4], data[5]));
	}

	return poses;
}

bool Scenario::TrialsCompleted(const TrialData& trialData) const
{
	bool allTrue = true;
	for (int i = 0; i < trialData.trialCompleted.size(); i++)
	{
		if (!trialData.trialCompleted[i])
		{
			allTrue = false;
			break;
		}
	}
	return allTrue;
}

void Scenario::SaveTrialData(const TrialData& trialData) const
{
	std::ofstream fileStream;
	fileStream.open(trialData.resultFile);
	for (int i = 0; i < trialData.trialSuccess.size(); i++)
	{
		if (trialData.trialSuccess[i])
			fileStream << "1";
		else
			fileStream << "0";
		fileStream << "\n";
	}
	fileStream.close();
}

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

#include <string>
#include <vector>
#include <map>
#include <random>
using std::string;
using std::vector;
using std::map;
using std::ostream;
using std::default_random_engine;
using std::uniform_real_distribution;
using std::random_device;

//enum class ScenarioTypes { BOOKS = 1, POWER_PLUG = 2, COFFEE_SUGAR = 3, GLASS_SUGAR = 4, FRIDGE = 5, CUBE_TOWER = 6, TABLE = 7, DRAWER = 8};
//enum class ObjectTypes { NONE = 0, BOOK = 1, BOTTLE = 2, CUP = 3, GLASS = 4, CYLINDER = 5 };

struct Pose
{
	FVector pos;
	FRotator rot;

	Pose() { }

	Pose(FVector position, FRotator rotation)
	{
		this->pos = FVector(position.X, position.Y, position.Z);
		this->rot = FRotator(rotation.Pitch, rotation.Yaw, rotation.Roll);
	}

	Pose(float x, float y, float z, float roll, float pitch, float yaw)
	{
		this->pos = FVector(x, y, z);
		this->rot = FRotator(pitch, yaw, roll);
	}

	Pose(const Pose& other)
	{
		this->pos = FVector(other.pos.X, other.pos.Y, other.pos.Z);
		this->rot = FRotator(other.rot.Pitch, other.rot.Yaw, other.rot.Roll);
	}

	Pose& operator=(const Pose& other)
	{
		if (this == &other)
			return *this;

		this->pos = FVector(other.pos.X, other.pos.Y, other.pos.Z);
		this->rot = FRotator(other.rot.Pitch, other.rot.Yaw, other.rot.Roll);
		return *this;
	}

	void SetPosition(FVector position)
	{
		this->pos = position;
	}

	void SetRotation(FRotator rotation)
	{
		this->rot = rotation;
	}

	void SetPose(FVector position, FRotator rotation)
	{
		this->pos = position;
		this->rot = rotation;
	}

	static bool EqualPosition(const Pose& pose1, const Pose& pose2, float translationEpsilon)
	{
		bool equalPosition = abs(pose1.pos.X - pose2.pos.X) < translationEpsilon
			&& abs(pose1.pos.Y - pose2.pos.Y) < translationEpsilon
			&& abs(pose1.pos.Z - pose2.pos.Z) < translationEpsilon;

		return equalPosition;
	}
};

struct RandomGenerator
{
	default_random_engine xGenerator;
	default_random_engine yGenerator;
	default_random_engine zGenerator;

	uniform_real_distribution<double>* xDistribution;
	uniform_real_distribution<double>* yDistribution;
	uniform_real_distribution<double>* zDistribution;

	void InitDistributions(FVector min, FVector max)
	{
		this->xGenerator.seed(random_device{}());
		this->yGenerator.seed(random_device{}());
		this->zGenerator.seed(random_device{}());

		this->xDistribution = new uniform_real_distribution<double>(min.X, max.X);
		this->yDistribution = new uniform_real_distribution<double>(min.Y, max.Y);
		this->zDistribution = new uniform_real_distribution<double>(min.Z, max.Z);
	}
};

struct RandomPoseGenerator
{
	RandomGenerator randomPos_gen;
	RandomGenerator randomRot_gen;

	void InitDistributions(FVector posMin, FVector posMax, FVector rotMin, FVector rotMax)
	{
		this->randomPos_gen.InitDistributions(posMin, posMax);
		this->randomRot_gen.InitDistributions(rotMin, rotMax);
	}

	Pose GeneratePose()
	{
		float x = (*this->randomPos_gen.xDistribution)(this->randomPos_gen.xGenerator);
		float y = (*this->randomPos_gen.yDistribution)(this->randomPos_gen.yGenerator);
		float z = (*this->randomPos_gen.zDistribution)(this->randomPos_gen.zGenerator);

		float roll = (*this->randomRot_gen.xDistribution)(this->randomRot_gen.xGenerator);
		float pitch = (*this->randomRot_gen.yDistribution)(this->randomRot_gen.yGenerator);
		float yaw = (*this->randomRot_gen.zDistribution)(this->randomRot_gen.zGenerator);

		return Pose(x, y, z, roll, pitch, yaw);
	}
};

struct MeshParams
{
	TCHAR* text;
	FVector scale;
	FVector comOffset;
	bool enablePhysics;
	bool enableGravity;
	float massScale;

	MeshParams()
	{
		this->text = TEXT("");
		this->scale = FVector(1, 1, 1);
		this->comOffset = FVector(0, 0, 0);
		this->enablePhysics = true;
		this->enableGravity = true;
		this->massScale = 1.0f;
	}

	MeshParams(TCHAR* text, FVector scale, bool enablePhysics, bool enableGravity, float massScale, FVector comOffset = FVector(0, 0, 0))
	{
		this->text = text;
		this->scale = scale;
		this->comOffset = comOffset;
		this->enablePhysics = enablePhysics;
		this->enableGravity = enableGravity;
		this->massScale = massScale;
	}
};

struct OptimisationParams
{
	string optimisationDataFile;
	string optimisedDataFile;
	string optimisationScript;
	string keysFile;
	string keys;
};

struct TrialData
{
	int numberOfTrials;
	int attemptsPerTrial;
	map<int, int> copyToTrialMap;
	vector<bool> trialSuccess;
	vector<bool> trialCompleted;
	vector<int> attemptCounters;
	int trialCounter;
	string resultFile;
};

struct ModelConfig
{
	ModelConfig() : massScale(1.0f), scale(-1.0f, -1.0f, -1.0f), comOffset(0.0f, 0.0f, 0.0f), simulatePhysics(true), enableGravity(true)
	{ }

	string name;
	string type;
	float massScale;
	bool simulatePhysics;
	FVector scale;
	FVector position;
	FRotator orientation;
	FVector comOffset;
	bool enableGravity;
};

struct ScenarioConfig
{
	string simulationType;
	string type;
	FVector posMin;
	FVector posMax;
	FVector rotMin;
	FVector rotMax;
	vector<ModelConfig> models;
	OptimisationParams optimisationParams;
    TrialData trialData;
};

struct DisplayConfig
{
	int displayRows;
	float rowOffset;
	float columnOffset;
	float floorOffset;
	int copiesPerFloor;
};

struct Tolerances
{
	float translationTolerance;
	float rotationTolerance;
	float translationEpsilon;
};

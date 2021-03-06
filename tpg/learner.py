from __future__ import division

import random
import time
import math
from bitarray import bitarray

from tpg.instruction import Instruction
from tpg.action import Action

"""
A Learner.
"""
class Learner:

    idCount = 0 # counter for id
    registerSize = 8 # size of registers

    def __init__(self, action, maxProgSize=8, randSeed=0, learner=None,
            makeNew=False, birthGen=0):

        if randSeed == 0:
            random.seed(int(round(time.time())))
        else:
            random.seed(randSeed)

        # reconstruct a learner
        if learner is not None:
            if makeNew: # make new from existing
                self.id = Learner.idCount
                Learner.idCount += 1
                self.birthGen = birthGen
                self.teamRefCount = 0
            else: # remake existing
                self.id = learner.id
                self.birthGen = learner.birthGen
                self.teamRefCount = learner.teamRefCount

            # these copied either way
            self.action = learner.action
            self.program = [i for i in learner.program]
            return

        # or make a brand new one
        self.id = Learner.idCount
        Learner.idCount += 1
        self.birthGen = birthGen
        self.action = Action(action)
        self.teamRefCount = 0
        self.program = [] # program is list of instructions

        # amount of instruction in program
        progSize = random.randint(1, maxProgSize)
        for i in range(progSize):
            ins = Instruction(randSeed=randSeed)
            self.program.append(ins)

    """
    Gets the bid from this learner based on the observation, bid being the
    weight this learner has in decision making (roughly).
    Args:
        obs:
            (Float[]) The current state of the environment.
        regDict:
            (Dict<Int,Float[]>) Dictionary of registers, find the registers of
            this learner with the key self.id. If None, uses default (all 0)
            register.
    Returns:
        (Float) The bid value.
    """
    def bid(self, obs, regDict=None):
        # choose register appropriately
        registers = None
        if regDict is None:
            registers = [0]*Learner.registerSize
        else:
            if self.id not in regDict:
                regDict[self.id] = [0]*Learner.registerSize
            registers = regDict[self.id]

        return 1 / (1 + math.exp(-runProgram(obs,registers)))

    """
    Runs this learner's program.
    Args:
        obs:
            (Float[]) The current state of the environment.
        registers:
            (Float[]) Registers to be used for doing calculations with.
    Returns:
        (Float) What the destination register's value is at the end.
    """
    def runProgram(self, obs, registers):
        # iterate over instructions in the program
        for inst in program:
            sourceVal = 0
            # first get an initial value from register or observation
            if Instruction.equalBitArrays(
                    inst.getBitArraySeg(Instruction.slcMode),Instruction.mode0):
                # instruction is mode0, source value comes from register
                sourceVal = registers[Instruction.getIntVal(
                    inst.getBitArraySeg(Instruction.slcSrc)) %
                        Learner.registerSize]
            else:
                # instruction not mode0, source value form obs
                sourceVal = obs[Instruction.getIntVal(
                    inst.getBitArraySeg(Instruction.slcSrc)) % len(obs)]

            # the operation to do on the register
            operation = inst.getBitArraySeg(Instruction.slcOp)
            # the register to fiddle with
            destReg = Instruction.getIntVal(
                inst.getBitArraySeg(Instruction.slcDest))

            if Instruction.equalBitArrays(operation, Instruction.opSum):
                registers[destReg] += sourceVal
            elif Instruction.equalBitArrays(operation, Instruction.opDiff):
                registers[destReg] -= sourceVal
            elif Instruction.equalBitArrays(operation, Instruction.opProd):
                registers[destReg] *= sourceVal
            elif Instruction.equalBitArrays(operation, Instruction.opDiv):
                registers[destReg] /= sourceVal
            elif Instruction.equalBitArrays(operation, Instruction.opCos):
                registers[destReg] = math.cos(sourceVal)
            elif Instruction.equalBitArrays(operation, Instruction.opLog):
                registers[destReg] = math.log(sourceVal)
            elif Instruction.equalBitArrays(operation, Instruction.opExp):
                registers[destReg] = math.exp(sourceVal)
            elif Instruction.equalBitArrays(operation, Instruction.opCond):
                if registers[destReg] < sourceVal:
                    registers[destReg] *= -1
            else:
                print("Invalid operation in learner.run")

            # default register to 0 if invalid value
            if (math.isnan(registers[destReg]) or
                    registers[destReg] == float('Inf')):
                registers[destReg] = 0

        return registers[0]

    """
    Mutates this learners program.
    Returns:
        (Bool) Whether actually mutated.
    """
    def mutateProgram(self, pProgramDelete, pProgramAdd, pProgramSwap,
            pProgramMutate, maxProgramSize):

        changed = False # whether a change occured

        # maybe delete instruction
        if (len(self.program) > 1 and random.uniform(0,1) < pProgramDelete):
            del self.program[random.choice(range(len(self.program)-1))]
            changed = True

        # maybe insert instruction
        if (len(self.program) < maxProgramSize and
                random.uniform(0,1) < pProgramAdd):
            ins = Instruction(randSeed=randSeed)
            self.program.insert(random.choice(range(len(self.program))))
            changed = True

        # maybe flip an instruction's bit
        if random.uniform(0,1) < pProgramMutate:
            self.program[random.choice(range(len(self.program)-1))].flip(
                    random.choice(range(Instruction.instructionSize-1)))
            changed = True

        # maybe swap two instructions
        if len(self.program) > 1 and random.uniform(0,1) < pProgramSwap:
            # indices to swap
            idx1 = random.choice(range(len(self.program)-1))
            idx2 = random.choice(
                    [x for x in range(len(self.program)-1) if x != idx1])
            # do swap
            tmp = self.program[idx1]
            self.program[idx1] = self.program[idx2]
            self.program[idx2] = tmp
            changed = True

        return changed

    """
    Changes the learners action to the argument action.
    Returns:
        (Bool) Whether the action is different after mutation.
    """
    def mutateAction(self, action):
        act = self.action
        self.action = action
        return act.equals(action)

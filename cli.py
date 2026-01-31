#!/usr/bin/env python3
"""
Red Team AI Command Line Interface
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import argparse
import json
from pathlib import Path
from shared import (
    ExperimentConfig,
    AgentRole,
    AttackStrategy,
    LLMProvider
)
from orchestrator import run_experiment


def load_config_from_file(config_path: str) -> ExperimentConfig:
    """Load experiment configuration from JSON file"""
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    return ExperimentConfig(**config_dict)


def create_config_interactive() -> ExperimentConfig:
    """Create configuration interactively"""
    print("\n🔴 Red Team AI - Create Experiment\n")
    
    # Basic info
    name = input("Experiment name: ")
    description = input("Description (optional): ")
    
    # Role
    print("\n--- Target Agent Role ---")
    role_name = input("Role name: ")
    role_desc = input("Role description: ")
    persona = input("Persona: ")
    
    print("Constraints (one per line, empty line to finish):")
    constraints = []
    while True:
        constraint = input("  ")
        if not constraint:
            break
        constraints.append(constraint)
    
    role = AgentRole(
        name=role_name,
        description=role_desc,
        persona=persona,
        constraints=constraints
    )
    
    # Strategies
    print("\n--- Attack Strategies ---")
    print("Available strategies:")
    strategies_list = [s.value for s in AttackStrategy]
    for i, s in enumerate(strategies_list, 1):
        print(f"  {i}. {s}")
    
    strategy_input = input("Select strategies (comma-separated numbers): ")
    selected_indices = [int(i.strip()) - 1 for i in strategy_input.split(",")]
    attack_strategies = [AttackStrategy(strategies_list[i]) for i in selected_indices]
    
    # Parameters
    print("\n--- Configuration ---")
    num_turns = int(input("Number of turns [10]: ") or "10")
    temp = float(input("Temperature [0.7]: ") or "0.7")
    
    return ExperimentConfig(
        experiment_name=name,
        description=description,
        target_role=role,
        attack_strategies=attack_strategies,
        num_turns=num_turns,
        temperature=temp
    )


def run_command(args):
    """Run experiment command"""
    if args.config:
        config = load_config_from_file(args.config)
    elif args.interactive:
        config = create_config_interactive()
    else:
        print("Error: Either --config or --interactive required")
        return 1
    
    print(f"\n🚀 Running experiment: {config.experiment_name}")
    
    result = run_experiment(config)
    
    print(f"\n✅ Experiment completed: {result.status}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    
    if result.scores:
        print(f"\n📊 Scores:")
        print(f"  Overall: {result.scores.overall_score:.3f}")
        print(f"  Role Fidelity: {result.scores.role_fidelity_score:.3f}")
        print(f"  Drift: {result.scores.drift_index:.3f}")
    
    # Save results
    if args.output:
        output_path = args.output
    else:
        output_path = f"result_{result.experiment_id}.json"
    
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(mode='json'), f, indent=2, default=str)
    
    print(f"\n💾 Results saved: {output_path}")
    
    return 0


def list_command(args):
    """List experiments command"""
    print("📋 Listing experiments...")
    print("(This requires database access)")
    # Would connect to database and list experiments
    return 0


def export_command(args):
    """Export experiment command"""
    print(f"📤 Exporting experiment {args.experiment_id}...")
    # Would load from database and export
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Red Team AI - RPLA Evaluation Platform CLI"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run an experiment')
    run_parser.add_argument('--config', '-c', help='Config file path')
    run_parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    run_parser.add_argument('--output', '-o', help='Output file path')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List experiments')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export experiment')
    export_parser.add_argument('experiment_id', help='Experiment ID')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json')
    export_parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Check for API key
    if args.command == 'run' and not os.getenv("GROQ_API_KEY"):
        print("⚠️  Error: GROQ_API_KEY not found in environment")
        return 1
    
    # Execute command
    if args.command == 'run':
        return run_command(args)
    elif args.command == 'list':
        return list_command(args)
    elif args.command == 'export':
        return export_command(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
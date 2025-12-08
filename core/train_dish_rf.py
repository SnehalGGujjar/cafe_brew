# menu/management/commands/train_dish_rf.py
from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from pathlib import Path
from menu.ml_rf import train_random_forest

class Command(BaseCommand):
    help = "Train Random Forest to predict dishes. Reads a CSV and saves model to menu_models/dish_rf.pkl"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            required=True,
            help="Path to training CSV (see ml_rf.py docstring for expected columns).",
        )
        parser.add_argument(
            "--target",
            type=str,
            default="dish_name",
            help="Target column name (default: dish_name).",
        )
        parser.add_argument(
            "--out",
            type=str,
            default="menu_models/dish_rf.pkl",
            help="Where to save the trained model (default: menu_models/dish_rf.pkl).",
        )

    def handle(self, *args, **opts):
        csv_path = Path(opts["csv"])
        if not csv_path.exists():
            raise CommandError(f"CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)
        result = train_random_forest(
            df=df,
            target_col=opts["target"],
            model_path=opts["out"],
        )

        self.stdout.write(self.style.SUCCESS(
            f" Trained RF saved to {result.model_path}\n"
            f"Accuracy: {result.accuracy:.4f}  |  F1-macro: {result.f1_macro:.4f}\n"
        ))
        self.stdout.write(result.report)

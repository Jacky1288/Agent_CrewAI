import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from crewai.tools import BaseTool
from crewai import LLM


class ChartGeneratorTool(BaseTool):
    name: str = "Create custom plots"
    description: str = (
        "Tool for automatically creating custom plots based on research results. "
        "Pass the full validated information gathered so far as a string."
    )

    def _run(self, research: str) -> str:
        try:
            extraction_prompt = f"""
            Analyze the research text and identify meaningful charts to visualize quantifiable data.
            For each chart provide a JSON object with: chart_type, x_axis, y_axis, color, Title, data.
            Return only a JSON array, no additional text.

            Text: {research}
            """
            llm = LLM(
                model=os.environ.get("OPENAI_MODEL_NAME", "deepseek-v4-flash"),
                base_url=os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE"),
                api_key=os.environ.get("OPENAI_API_KEY"),
            )
            response = llm.call([{"role": "user", "content": extraction_prompt}])
            response = response.strip().removeprefix("```json").removesuffix("```").strip()

            charts_data = json.loads(response)
            if not isinstance(charts_data, list) or len(charts_data) == 0:
                return "No quantifiable data found to visualize."

            os.makedirs("plots", exist_ok=True)
            plots_created = []

            for i, chart_info in enumerate(charts_data):
                try:
                    chart_type = chart_info.get("chart_type", "bar").lower()
                    x_axis = chart_info.get("x_axis", "x")
                    y_axis = chart_info.get("y_axis", "y")
                    title = chart_info.get("Title", f"Chart {i+1}")
                    hue = chart_info.get("color", None)
                    df = pd.DataFrame(chart_info.get("data", {}))
                    if df.empty:
                        continue

                    plt.figure(figsize=(10, 6))
                    if chart_type == "line":
                        sns.lineplot(data=df, x=x_axis, y=y_axis, marker="o", hue=hue)
                    elif chart_type in ["bar", "column"]:
                        sns.barplot(data=df, x=x_axis, y=y_axis, hue=hue)
                    elif chart_type == "scatter":
                        sns.scatterplot(data=df, x=x_axis, y=y_axis, hue=hue)
                    elif chart_type == "pie":
                        plt.pie(df[y_axis], labels=df[x_axis], autopct='%1.1f%%')
                        plt.axis('equal')

                    plt.title(title)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    filename = f"plots/plot_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    plt.savefig(filename, dpi=300, bbox_inches='tight')
                    plt.close()
                    plots_created.append(filename)
                except Exception as e:
                    print(f"Error creating chart {i+1}: {e}")

            return f"Created {len(plots_created)} plots: {', '.join(plots_created)}" if plots_created else "No plots created."

        except json.JSONDecodeError as e:
            return f"JSON parse error: {e}"
        except Exception as e:
            return f"Error: {e}"
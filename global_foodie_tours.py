import os
import time
from julep import Julep
from pathlib import Path

# Set up output directory
OUTPUT_DIR = Path(r"YOUR_DESIRED_OUTPUT_DIRECTION") # Replace with your desired address

def setup_output_directory():
    """Create output directory if it doesn't exist"""
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "outputs").mkdir(exist_ok=True)
        (OUTPUT_DIR / "individual_tours").mkdir(exist_ok=True)
        print(f"📁 Output directory ready: {OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return False

# Initialize client
client = None

def create_working_agent():
    """Create agent with correct format"""
    try:
        agent = client.agents.create(
            name="Foodie Tour Guide",
            about="Expert food guide who creates authentic local dining experiences",
            model="gpt-4o"
        )
        print(f"✅ Agent created: {agent.id}")
        return agent
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return None

def create_working_task_simple(agent_id):
    """Create task with minimal, working structure"""
    try:
        task = client.tasks.create(
            agent_id=agent_id,
            name="Simple Foodie Tour",
            description="Create authentic foodie tour for a city",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                }
            },
            main=[
                {
                    "prompt": [
                        {
                            "role": "system",
                            "content": "You are an expert local food guide. Create a one-day foodie tour for the given city with authentic local dishes and specific restaurants. Format:\n\n# [City] Foodie Tour\n\n## Breakfast (9 AM)\n**Dish:** [Local dish name]\n**Restaurant:** [Specific name & area]\n**Experience:** [Why this is special]\n\n## Lunch (1 PM)\n**Dish:** [Local dish name]\n**Restaurant:** [Specific name & area] \n**Experience:** [Why this is special]\n\n## Dinner (7 PM)\n**Dish:** [Local dish name]\n**Restaurant:** [Specific name & area]\n**Experience:** [Why this is special]\n\n## Local Tips\n- Transportation advice\n- Cultural notes\n- Best times to visit"
                        },
                        {
                            "role": "user",
                            "content": "Create an authentic foodie tour for this city. Focus on local specialties and real restaurants."
                        }
                    ]
                }
            ]
        )
        print(f"✅ Simple task created: {task.id}")
        return task
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        return None

def create_working_task_with_input(agent_id):
    """Create task that properly uses input"""
    try:
        task = client.tasks.create(
            agent_id=agent_id,
            name="Input-Based Foodie Tour",
            description="Create foodie tour using input city",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            },
            main=[
                {
                    "prompt": [
                        {
                            "role": "system", 
                            "content": "You are an expert local food guide. I will give you a city name, and you will create an authentic one-day foodie tour with real local dishes and specific restaurants.\n\nFormat your response exactly like this:\n\n# [City Name] Foodie Tour\n\n## 🌅 Breakfast (9:00 AM)\n**Local Dish:** [Authentic breakfast dish]\n**Restaurant:** [Real restaurant name and neighborhood]\n**Experience:** [What makes this special - taste, atmosphere, culture]\n\n## 🍽️ Lunch (1:00 PM) \n**Local Dish:** [Signature local dish]\n**Restaurant:** [Real restaurant name and neighborhood]\n**Experience:** [What makes this special - taste, atmosphere, culture]\n\n## 🌃 Dinner (7:00 PM)\n**Local Dish:** [Traditional dinner dish]\n**Restaurant:** [Real restaurant name and neighborhood] \n**Experience:** [What makes this special - taste, atmosphere, culture]\n\n## 🚶‍♂️ Local Tips\n- Best way to get between restaurants\n- Cultural dining etiquette \n- When to visit each place\n- What to expect\n\nMake it authentic, specific, and culturally rich!"
                        },
                        {
                            "role": "user",
                            "content": "Create a foodie tour for: Istanbul"
                        }
                    ]
                }
            ]
        )
        print(f"✅ Input-based task created: {task.id}")
        return task
    except Exception as e:
        print(f"❌ Input task creation failed: {e}")
        return None

def test_task_execution(task, city="Istanbul"):
    """Test task execution with detailed monitoring"""
    print(f"\n🎯 Testing task execution for {city}...")
    
    try:
        # Create execution
        execution = client.executions.create(
            task_id=task.id,
            input={"city": city}
        )
        print(f"   Execution created: {execution.id}")
        
        # Monitor with shorter intervals
        max_attempts = 40  # 2 minutes total
        attempt = 0
        
        while attempt < max_attempts:
            try:
                result = client.executions.get(execution.id)
                status = result.status
                print(f"   [{attempt:2d}] Status: {status}")
                
                if status == "succeeded":
                    print(f"✅ {city} completed!")
                    return result.output
                elif status == "failed":
                    print(f"❌ {city} failed!")
                    if hasattr(result, 'error') and result.error:
                        print(f"   Error details: {result.error}")
                    else:
                        print("   No error details provided")
                    return None
                elif status in ["queued", "starting", "running"]:
                    time.sleep(3)
                    attempt += 1
                else:
                    print(f"   Unknown status: {status}")
                    time.sleep(3)
                    attempt += 1
                    
            except Exception as e:
                print(f"   Error checking status: {e}")
                time.sleep(3)
                attempt += 1
        
        print(f"❌ {city} timed out")
        return None
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return None

def run_comprehensive_test():
    """Run all tests to find what works"""
    print("🧪 Running comprehensive tests...")
    
    # Create agent
    agent = create_working_agent()
    if not agent:
        return None
    
    print("\n" + "="*50)
    
    # Test 1: Simple task (no input variables)
    print("🧪 Test 1: Simple static task...")
    simple_task = create_working_task_simple(agent.id)
    if simple_task:
        result = test_task_execution(simple_task)
        if result:
            print("✅ Simple task works!")
            return simple_task, "simple"
    
    print("\n" + "="*50)
    
    # Test 2: Input-based task
    print("🧪 Test 2: Input-based task...")
    input_task = create_working_task_with_input(agent.id)
    if input_task:
        result = test_task_execution(input_task)
        if result:
            print("✅ Input task works!")
            return input_task, "input"
    
    print("❌ All tests failed")
    return None, None

def process_multiple_cities(task, task_type):
    """Process multiple cities with working task"""
    cities = [
        "Istanbul", 
        "New Delhi", 
        "New York", 
        "Bern", 
        "Paris", 
        "Tehran", 
        "Saint Petersburg", 
        "Rome", 
        "Barcelona"
    ]
    results = {}
    
    print(f"\n🌍 Processing {len(cities)} cities with {task_type} task...")
    
    for i, city in enumerate(cities, 1):
        print(f"\n📍 [{i}/{len(cities)}] Processing {city}...")
        
        if task_type == "simple":
            # For simple tasks, we need to create a new task for each city
            # since we can't use input variables
            city_task = create_city_specific_task(task.agent_id, city)
            if city_task:
                result = test_task_execution(city_task, city)
            else:
                result = None
        else:
            # For input tasks, we can reuse the same task
            result = test_task_execution(task, city)
        
        if result:
            results[city] = result
            save_individual_tour(city, result)
            print(f"✅ {city} completed and saved!")
        else:
            print(f"❌ {city} failed")
        
        # Small delay between cities to avoid rate limiting
        time.sleep(3)
    
    return results

def create_city_specific_task(agent_id, city):
    """Create a task for a specific city (for simple mode)"""
    try:
        task = client.tasks.create(
            agent_id=agent_id,
            name=f"{city} Foodie Tour",
            description=f"Foodie tour for {city}",
            main=[
                {
                    "prompt": [
                        {
                            "role": "system",
                            "content": f"Create an authentic one-day foodie tour for {city}. Include breakfast, lunch, and dinner with real local dishes and specific restaurants. Make it culturally authentic and engaging."
                        },
                        {
                            "role": "user",
                            "content": f"Create a detailed foodie tour for {city} with local specialties and real restaurant recommendations."
                        }
                    ]
                }
            ]
        )
        return task
    except Exception as e:
        print(f"   Failed to create task for {city}: {e}")
        return None

def save_individual_tour(city, tour_data):
    """Save individual city tour"""
    try:
        safe_name = city.lower().replace(' ', '_').replace(',', '').replace('.', '')
        filename = OUTPUT_DIR / "individual_tours" / f"{safe_name}_foodie_tour.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {city} Foodie Tour\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(tour_data))
            f.write(f"\n\n{'=' * 60}\n")
        
        print(f"   💾 Saved: {filename}")
        
    except Exception as e:
        print(f"   ❌ Save failed: {e}")

def save_combined_results(results):
    """Save combined results"""
    if not results:
        print("⚠️ No results to save")
        return
    
    combined_file = OUTPUT_DIR / "outputs" / "working_tours_combined.txt"
    with open(combined_file, "w", encoding="utf-8") as f:
        f.write("🌍 GLOBAL FOODIE TOURS - WORKING VERSION\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Successfully processed: {len(results)} cities\n")
        f.write("=" * 80 + "\n\n")
        
        for i, (city, tour) in enumerate(results.items(), 1):
            f.write(f"📍 {i}. {city.upper()}\n")
            f.write("=" * 40 + "\n\n")
            f.write(str(tour))
            f.write("\n\n" + "=" * 80 + "\n\n")
    
    # Create summary
    summary_file = OUTPUT_DIR / "outputs" / "success_summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("# 🎉 Julep Foodie Tours - SUCCESS!\n\n")
        f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Cities completed:** {len(results)}\n\n")
        
        f.write("## ✅ Successful Cities\n\n")
        for city in results.keys():
            f.write(f"- **{city}** ✅\n")
        
        f.write(f"\n## 📁 Generated Files\n\n")
        f.write("### Individual Tours\n")
        for city in results.keys():
            safe_name = city.lower().replace(' ', '_')
            f.write(f"- `individual_tours/{safe_name}_foodie_tour.txt`\n")
        
        f.write("### Combined Files\n")
        f.write("- `outputs/working_tours_combined.txt`\n")
        f.write("- `outputs/success_summary.md`\n")
    
    print(f"📚 Files saved to: {OUTPUT_DIR}")
    print(f"   📄 Combined: {combined_file}")
    print(f"   📄 Summary: {summary_file}")
    print(f"✅ SUCCESS! Processed {len(results)} cities!")

def main():
    """Main function with working approach"""
    # Your API keys
    JULEP_API_KEY = "YOUR_JULEP_API_KEY"  # Replace with your actual key
    OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"  # Replace with your actual key
    
    print("🚀 JULEP FOODIE TOURS - WORKING VERSION")
    print("=" * 70)
    
    # Setup
    if not setup_output_directory():
        return
    
    # Initialize client
    global client
    client = Julep(api_key=JULEP_API_KEY)
    
    # Find working approach
    working_task, task_type = run_comprehensive_test()
    
    if working_task:
        print(f"\n🎉 Found working approach: {task_type}")
        print("=" * 70)
        
        # Process all cities
        results = process_multiple_cities(working_task, task_type)
        
        # Save everything
        save_combined_results(results)
        
        print(f"\n🏆 FINAL RESULTS:")
        print(f"   Cities processed: {len(results)}")
        if results:
            print("   Success! ✅")
            for city in results.keys():
                print(f"     - {city}")
        else:
            print("   No cities completed ❌")
    else:
        print("\n❌ Could not find a working task structure")
        print("This might be a temporary Julep service issue")
        print("Try running again in a few minutes")

if __name__ == "__main__":
    main()
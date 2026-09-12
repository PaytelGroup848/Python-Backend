import asyncio
from datetime import datetime
from sqlalchemy import select, text
from app.db.database import AsyncSessionLocal, engine, Base
import app.main  # noqa - registers all models on Base.metadata

from app.modules.training_providers.models.training_provider import TrainingProvider
from app.models.model import ModelRegistry
from app.models.model_version import ModelVersion
from app.modules.training.models.training_configuration import TrainingConfiguration
from app.modules.tokenizers.models.tokenizer import Tokenizer
from app.modules.tokenizers.models.tokenizer_version import TokenizerVersion
from app.models.provider import Provider
from app.models.assistant import Assistant
from app.modules.billing.models.plan import Plan
from app.modules.billing.models.plan_version import PlanVersion
from app.modules.billing.models.plan_price import PlanPrice
from app.modules.corpora.models.corpus import Corpus
from app.modules.storage_registry.models.storage_implementation import StorageImplementation
from app.modules.storage_registry.models.storage_instance import StorageInstance
from app.shared.constants.storage_scope_type import StorageScopeType

async def seed_defaults():
    print("[SEED] Ensuring pgvector extension and database tables exist...")
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))

    async with AsyncSessionLocal() as db:
        print("[SEED] Starting platform database seeding...")

        # -3. Seed Default Storage Implementation & Instance
        impl_res = await db.execute(select(StorageImplementation).where(StorageImplementation.implementation_code == "LOCAL_FILESYSTEM"))
        impl = impl_res.scalars().first()
        if not impl:
            impl = StorageImplementation(
                implementation_code="LOCAL_FILESYSTEM",
                implementation_version="1.0",
                display_name="Local Filesystem Storage",
                description="Default Local Disk Storage Provider",
                runtime_type="LOCAL",
                configuration_schema_json={},
                capabilities_json={"read": True, "write": True, "delete": True},
                is_active=True
            )
            db.add(impl)
            await db.flush()
            print("[SEED] Added Storage Implementation: LOCAL_FILESYSTEM")

        inst_res = await db.execute(select(StorageInstance).where(StorageInstance.instance_code == "PLATFORM_PIPELINE_STORAGE"))
        inst = inst_res.scalars().first()
        if not inst:
            inst = StorageInstance(
                storage_implementation_id=impl.id,
                scope_type=StorageScopeType.PLATFORM.value,
                instance_code="PLATFORM_PIPELINE_STORAGE",
                display_name="Platform Pipeline Dataset Storage",
                configuration_json={"root_directory": "/data/platform_storage"},
                is_active=True
            )
            db.add(inst)
            await db.flush()
            print("[SEED] Added Storage Instance: PLATFORM_PIPELINE_STORAGE")
        else:
            setattr(inst, "configuration_json", {"root_directory": "/data/platform_storage"})
            await db.flush()

        # -2. Seed Default Knowledge Corpora
        corpora_items = [
            {"id": 1, "name": "Legal Knowledge Corpus", "domain": "legal", "description": "Indian Penal Code, Statutory Acts & Legal Case Laws", "status": "ACTIVE"},
            {"id": 2, "name": "General Knowledge Corpus", "domain": "general", "description": "Universal Multi-Domain Knowledge Base", "status": "ACTIVE"},
            {"id": 3, "name": "Vedic Astrology Corpus", "domain": "astrology", "description": "Vedic Astrology & Planetary Transit Rules", "status": "ACTIVE"},
            {"id": 4, "name": "Software Engineering Corpus", "domain": "coding", "description": "Fullstack Architecture & Code References", "status": "ACTIVE"},
            {"id": 5, "name": "Clinical Medical Corpus", "domain": "medical", "description": "Healthcare & Clinical Guidelines", "status": "ACTIVE"},
        ]

        for citem in corpora_items:
            c_res = await db.execute(select(Corpus).where(Corpus.id == citem["id"]))
            c_obj = c_res.scalars().first()
            if not c_obj:
                c_obj = Corpus(
                    id=citem["id"],
                    name=citem["name"],
                    domain=citem["domain"],
                    description=citem["description"],
                    status=citem["status"]
                )
                db.add(c_obj)
                await db.flush()
                print(f"[SEED] Added Corpus: {citem['name']}")

        # -1. Seed Subscription Plans & Limits
        plan_res = await db.execute(select(Plan).where(Plan.plan_code == "free"))
        free_plan = plan_res.scalars().first()
        if not free_plan:
            free_plan = Plan(
                plan_code="free",
                plan_name="Free Tier",
                description="Default Free Plan with 1,000,000 monthly tokens",
                is_public=True,
                is_active=True
            )
            db.add(free_plan)
            await db.flush()
            print("[SEED] Added Free Subscription Plan")

            free_version = PlanVersion(
                plan_id=free_plan.id,
                version_number=1,
                monthly_token_limit=10000000,
                monthly_request_limit=100000,
                monthly_cost_limit=0,
                is_active=True
            )
            db.add(free_version)
            await db.flush()
            print("[SEED] Added Free Plan Version Limits")

        # Seed Pro Tier Plan
        pro_res = await db.execute(select(Plan).where(Plan.plan_code == "pro"))
        pro_plan = pro_res.scalars().first()
        if not pro_plan:
            pro_plan = Plan(
                plan_code="pro",
                plan_name="Pro Tier Plan",
                description="Professional plan with 50M tokens/month and Tax Invoice support",
                is_public=True,
                is_active=True
            )
            db.add(pro_plan)
            await db.flush()

            pro_version = PlanVersion(
                plan_id=pro_plan.id,
                version_number=1,
                monthly_token_limit=50000000,
                monthly_request_limit=500000,
                monthly_cost_limit=18054,
                is_active=True
            )
            db.add(pro_version)
            await db.flush()
            print("[SEED] Added Pro Tier Plan & Version")

        # Seed Enterprise Tier Plan
        ent_res = await db.execute(select(Plan).where(Plan.plan_code == "enterprise"))
        ent_plan = ent_res.scalars().first()
        if not ent_plan:
            ent_plan = Plan(
                plan_code="enterprise",
                plan_name="Enterprise Tier Plan",
                description="Unlimited high-capacity enterprise subscription with priority RAG compute",
                is_public=True,
                is_active=True
            )
            db.add(ent_plan)
            await db.flush()

            ent_version = PlanVersion(
                plan_id=ent_plan.id,
                version_number=1,
                monthly_token_limit=250000000,
                monthly_request_limit=2000000,
                monthly_cost_limit=117941,
                is_active=True
            )
            db.add(ent_version)
            await db.flush()
            print("[SEED] Added Enterprise Tier Plan & Version")


        # 0. Seed AI Assistants (General Chat, LawGPT, Astrology, Coder, Medical)
        assistant_items = [
            {
                "code": "general",
                "name": "General Chat",
                "description": "Universal AI Assistant for general knowledge and multi-domain tasks",
                "system_prompt": "You are General Chat, a helpful, versatile universal AI assistant. You can answer general knowledge and multi-domain questions in a helpful and friendly manner."
            },
            {
                "code": "lawgpt",
                "name": "LawGPT",
                "description": "Indian Legal Advisor, IPC 1860, Constitution & Statutory Legal Assistant",
                "system_prompt": "You are LawGPT, an expert Indian legal AI assistant. You answer queries strictly regarding Indian Penal Code, Constitution of India, Supreme Court precedents, and legal procedures. You MUST ONLY answer legal questions. If the user asks ANY question outside the legal domain (e.g. coding, cooking, astrology, entertainment, medical, casual topics), you MUST politely refuse by stating: 'Main LawGPT hoon aur sirf kanoon (Law) sambandhit sawalon ke jawab de sakta hoon. Kripya kanoon se juda sawal puchein.' Do not answer non-legal queries."
            },
            {
                "code": "astrology",
                "name": "Astrology AI",
                "description": "Vedic Astrology, Kundli Analysis & Horoscope Insights Specialist",
                "system_prompt": "You are Astrology AI, an expert in Vedic astrology, planetary transits, and horoscope calculations. You MUST ONLY answer questions regarding Vedic astrology, kundli, horoscopes, and planetary positions. If the user asks ANY question outside astrology (e.g. law, medical, coding, cooking), you MUST politely refuse by stating: 'Main Astrology AI hoon aur sirf jyotish evam kundli sambandhit sawalon ke jawab de sakta hoon. Kripya jyotish se juda sawal puchein.' Do not answer non-astrology queries."
            },
            {
                "code": "coder",
                "name": "Code Architect",
                "description": "Fullstack Software Engineering, System Architecture & Code Debugging Specialist",
                "system_prompt": "You are Code Architect, an elite software engineering AI specializing in production web applications, system design, and clean code. You MUST ONLY answer programming, software engineering, and technical architecture questions. If the user asks ANY question outside technology and programming (e.g. law, medical, astrology), you MUST politely refuse by stating: 'Main Code Architect hoon aur sirf coding evam software engineering sambandhit sawalon ke jawab de sakta hoon. Kripya programming se juda sawal puchein.' Do not answer non-programming queries."
            },
            {
                "code": "medical",
                "name": "MedAssist AI",
                "description": "Clinical Knowledge, Symptom Pre-screening & Healthcare Information Specialist",
                "system_prompt": "You are MedAssist AI, a clinical and healthcare information specialist. You MUST ONLY answer healthcare, medical, clinical, and wellness queries. If the user asks ANY question outside healthcare (e.g. law, astrology, coding, recipes), you MUST politely refuse by stating: 'Main MedAssist AI hoon aur sirf medical evam health sambandhit sawalon ke jawab de sakta hoon. Kripya health se juda sawal puchein.' Do not answer non-medical queries."
            }
        ]

        for item in assistant_items:
            asst_res = await db.execute(select(Assistant).where(Assistant.code == item["code"]))
            asst_obj = asst_res.scalars().first()
            if not asst_obj:
                now = datetime.utcnow()
                asst_obj = Assistant(
                    code=item["code"],
                    name=item["name"],
                    description=item["description"],
                    system_prompt=item["system_prompt"],
                    is_active=True,
                    created_at=now,
                    updated_at=now
                )
                db.add(asst_obj)
                await db.flush()
                print(f"[SEED] Added AI Assistant: {item['name']}")

        # 1. Seed AI Provider if not exists
        provider_res = await db.execute(select(Provider).limit(1))
        provider = provider_res.scalars().first()
        if not provider:
            now = datetime.utcnow()
            provider = Provider(
                code="SYSTEM",
                name="System AI Provider",
                provider_class="app.services.system_provider.SystemProvider",
                is_active=True,
                priority=100,
                created_at=now,
                updated_at=now
            )
            db.add(provider)
            await db.flush()
            print(f"[SEED] Added Default AI Provider (ID: {provider.id})")

        # 2. Seed Training Provider
        tp_res = await db.execute(select(TrainingProvider).where(TrainingProvider.code == "NATIVE_PYTORCH"))
        tp = tp_res.scalars().first()
        if not tp:
            tp = TrainingProvider(
                code="NATIVE_PYTORCH",
                display_name="Native PyTorch Runtime",
                runtime_version="1.0.0",
                provider_type="LOCAL",
                runtime_class="app.modules.training_runtime.providers.native_training_runtime.NativeTrainingRuntime",
                capabilities={"fine_tuning": True, "lora": True},
                runtime_components={},
                is_active=True
            )
            db.add(tp)
            await db.flush()
            print("[SEED] Added Training Provider: Native PyTorch Runtime")

        # 3. Seed Base Models & Versions
        models_data = [
            ("llama3-8b", "LLaMA-3-8B-Instruct", "Meta LLaMA 3 8B Base Model"),
            ("mistral-7b", "Mistral-7B-Instruct", "Mistral AI 7B Base Model"),
            ("qwen2.5-7b", "Qwen2.5-7B-Instruct", "Qwen 2.5 7B Base Model"),
        ]

        for code, display_name, description in models_data:
            m_res = await db.execute(select(ModelRegistry).where(ModelRegistry.code == code))
            model_obj = m_res.scalars().first()
            if not model_obj:
                model_obj = ModelRegistry(
                    code=code,
                    display_name=display_name,
                    description=description,
                    provider_id=provider.id,
                    status="ACTIVE",
                    is_active=True
                )
                db.add(model_obj)
                await db.flush()
                print(f"[SEED] Added Base Model: {display_name}")

                # Seed Model Version
                mv_res = await db.execute(select(ModelVersion).where(ModelVersion.model_id == model_obj.id))
                mv_obj = mv_res.scalars().first()
                if not mv_obj:
                    mv_obj = ModelVersion(
                        model_id=model_obj.id,
                        version="v1.0.0",
                        display_name="v1.0.0 Base Version",
                        description="Initial Base Version",
                        status="ACTIVE",
                        is_active=True
                    )
                    db.add(mv_obj)
                    await db.flush()
                    print(f"[SEED] Added Model Version v1.0.0 for {display_name}")

        # 4. Seed Training Configuration
        tc_res = await db.execute(select(TrainingConfiguration).limit(1))
        tc_obj = tc_res.scalars().first()
        if not tc_obj:
            tc_obj = TrainingConfiguration(
                configuration_code="DEFAULT_SFT",
                display_name="Standard SFT Configuration",
                description="Default Supervised Fine-Tuning Hyperparameters",
                configuration_json={
                    "training": {
                        "data_batch_size": 4,
                        "epochs": 3,
                        "learning_rate": 0.0002,
                        "optimizer": "adamw"
                    },
                    "formatter": {"type": "prompt_completion"},
                    "tokenizer": {"type": "auto"},
                    "training_strategy": {
                        "strategy_class": "app.modules.training_runtime.strategies.causal_language_model_strategy.CausalLanguageModelStrategy",
                        "configuration": {
                            "learning_rate": 0.0002,
                            "epochs": 3
                        }
                    },
                    "checkpoint": {"enabled": False}
                },
                version=1,
                training_type="SFT",
                runtime_code="NATIVE_PYTORCH",
                is_system=True,
                is_active=True,
                created_by="system"
            )
            db.add(tc_obj)
            await db.flush()
            print("[SEED] Added Default Training Configuration")

        # 5. Seed Tokenizer & Version
        tok_res = await db.execute(select(Tokenizer).limit(1))
        tok_obj = tok_res.scalars().first()
        if not tok_obj:
            tok_obj = Tokenizer(
                code="PLATFORM_SUBWORD",
                display_name="Platform Subword Tokenizer",
                status="ACTIVE",
                is_active=True
            )
            db.add(tok_obj)
            await db.flush()
            print("[SEED] Added Tokenizer")

            tok_ver = TokenizerVersion(
                tokenizer_id=tok_obj.id,
                version="v1.0.0",
                display_name="v1.0.0 Subword Tokenizer",
                vocabulary_size=32000,
                content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                source_type="HUGGINGFACE",
                source_uri="gpt2",
                source_revision="main",
                status="ACTIVE",
                is_active=True
            )
            db.add(tok_ver)
            await db.flush()
            print("[SEED] Added Tokenizer Version")

        # 6. Seed Default Billing Plans (Idempotent: Free, Pro, Enterprise)
        plans_seed_data = [
            {
                "code": "free",
                "name": "Free Tier",
                "description": "Essential AI features for personal exploration & experimentation",
                "is_public": True,
                "token_limit": 20000,
                "request_limit": 100,
                "cost_limit": 0.0,
                "prices": [
                    {"cycle": "monthly", "amount": 0.0, "currency": "INR", "provider": "razorpay"},
                ]
            },
            {
                "code": "pro",
                "name": "Pro Plan",
                "description": "Full access to frontier models, developer keys, and priority generation",
                "is_public": True,
                "token_limit": 1000000,
                "request_limit": 5000,
                "cost_limit": 0.0,
                "prices": [
                    {"cycle": "monthly", "amount": 799.0, "currency": "INR", "provider": "razorpay"},
                    {"cycle": "yearly", "amount": 7990.0, "currency": "INR", "provider": "razorpay"},
                ]
            },
            {
                "code": "enterprise",
                "name": "Enterprise",
                "description": "Maximum scale, dedicated capacity & custom pipeline integration",
                "is_public": True,
                "token_limit": 5000000,
                "request_limit": 25000,
                "cost_limit": 0.0,
                "prices": [
                    {"cycle": "monthly", "amount": 2499.0, "currency": "INR", "provider": "razorpay"},
                    {"cycle": "yearly", "amount": 24990.0, "currency": "INR", "provider": "razorpay"},
                ]
            }
        ]

        for pdata in plans_seed_data:
            p_res = await db.execute(select(Plan).where(Plan.plan_code == pdata["code"]))
            p_obj = p_res.scalars().first()
            if not p_obj:
                now = datetime.utcnow()
                p_obj = Plan(
                    plan_code=pdata["code"],
                    plan_name=pdata["name"],
                    description=pdata["description"],
                    is_public=pdata["is_public"],
                    is_active=True,
                    created_at=now
                )
                db.add(p_obj)
                await db.flush()

                v_obj = PlanVersion(
                    plan_id=p_obj.id,
                    version_number=1,
                    monthly_token_limit=pdata["token_limit"],
                    monthly_request_limit=pdata["request_limit"],
                    monthly_cost_limit=pdata["cost_limit"],
                    is_active=True,
                    created_at=now
                )
                db.add(v_obj)
                await db.flush()

                for pr in pdata["prices"]:
                    price_obj = PlanPrice(
                        plan_version_id=v_obj.id,
                        provider=pr["provider"],
                        billing_cycle=pr["cycle"],
                        currency=pr["currency"],
                        amount=pr["amount"],
                        is_active=True,
                        created_at=now
                    )
                    db.add(price_obj)
                await db.flush()
                print(f"[SEED] Added Plan: {pdata['name']} (v1) with prices")
            else:
                v_res = await db.execute(
                    select(PlanVersion)
                    .where(PlanVersion.plan_id == p_obj.id, PlanVersion.is_active == True)
                    .order_by(PlanVersion.version_number.desc())
                )
                v_obj = v_res.scalars().first()
                if not v_obj:
                    v_obj = PlanVersion(
                        plan_id=p_obj.id,
                        version_number=1,
                        monthly_token_limit=pdata["token_limit"],
                        monthly_request_limit=pdata["request_limit"],
                        monthly_cost_limit=pdata["cost_limit"],
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    db.add(v_obj)
                    await db.flush()

                for pr in pdata["prices"]:
                    pr_res = await db.execute(
                        select(PlanPrice).where(
                            PlanPrice.plan_version_id == v_obj.id,
                            PlanPrice.billing_cycle == pr["cycle"],
                            PlanPrice.is_active == True
                        )
                    )
                    if not pr_res.scalars().first():
                        db.add(PlanPrice(
                            plan_version_id=v_obj.id,
                            provider=pr["provider"],
                            billing_cycle=pr["cycle"],
                            currency=pr["currency"],
                            amount=pr["amount"],
                            is_active=True,
                            created_at=datetime.utcnow()
                        ))
                        print(f"[SEED] Added missing price {pr['cycle']} (INR {pr['amount']}) for {pdata['name']}")
                await db.flush()

        await db.commit()
        print("[SEED] Seeding completed successfully! All dropdowns are now database-populated.")

if __name__ == "__main__":
    asyncio.run(seed_defaults())

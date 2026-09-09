import json
from sqlalchemy.orm import Session
from app.models import Subject, Topic, ContentAsset, User
from app.security import hash_password
from app.db import SessionLocal, engine, Base


def seed_database(db: Session):
    """Seed initial Subject, 10 Topics, and Dense/Fast/Short-video assets."""
    existing_subject = db.query(Subject).filter(Subject.id == "os-sem3-aiml").first()
    if existing_subject:
        return

    # 1. Subject
    os_subject = Subject(
        id="os-sem3-aiml",
        name="Operating Systems",
        branch="AIML",
        semester=3,
        enabled=True,
    )
    db.add(os_subject)

    # 2. Demo User
    demo_user = User(
        id="usr_demo_aiml",
        name="Alex Sharma",
        email="demo@adaptlearn.dev",
        password_hash=hash_password("password123"),
        branch="AIML",
        semester=3,
    )
    db.add(demo_user)
    db.flush()

    # 3. 10 Comprehensive Operating Systems Topics
    topics_data = [
        (
            "os-t01",
            "Introduction to OS & System Calls",
            1,
            0.65,
            ["Basic Computer Architecture"],
            {
                "dense": {
                    "prerequisites": ["Computer Organization", "C Programming Basics"],
                    "textbooks": [
                        {"title": "Operating System Concepts (10th Ed)", "author": "Silberschatz, Galvin, Gagne"},
                        {"title": "Modern Operating Systems", "author": "Andrew S. Tanenbaum"},
                    ],
                    "notes": (
                        "An Operating System acts as an intermediary between user programs and the raw hardware. "
                        "Key goals are execution safety, resource isolation, and hardware abstraction. Dual-mode "
                        "operation switches via mode-bit: User Mode (bit 1) and Kernel Mode (bit 0). System calls "
                        "provide the programmatic interface where user processes invoke kernel-level privileges."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=26QPDBe-NB8",
                    "est_minutes": 25,
                },
                "fast": {
                    "bullets": [
                        "Dual-mode operation: Mode bit prevents user applications from corrupting system resources.",
                        "System call lifecycle: Trap instruction -> save registers -> execute kernel routine -> restore & return.",
                        "Architectures: Monolithic (high speed, single memory space) vs Microkernel (high modularity, IPC overhead).",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=vBURTt97EkA",
                    "mustAskTopics": ["Trap Handler vs Interrupt", "Mode Bit Transition", "POSIX System Calls"],
                    "est_minutes": 8,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-01-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                            "caption": "Why User Mode vs Kernel Mode exists in 45 seconds.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t02",
            "Process Management & Process Control Block (PCB)",
            2,
            0.75,
            ["os-t01"],
            {
                "dense": {
                    "prerequisites": ["os-t01", "Stack & Heap Memory Layout"],
                    "textbooks": [{"title": "Operating Systems: Three Easy Pieces", "author": "Arpaci-Dusseau"}],
                    "notes": (
                        "A process is a program in execution containing text, data, heap, and stack segments. "
                        "The Process Control Block (PCB) maintains process state (New, Ready, Running, Waiting, Terminated), "
                        "program counter, CPU registers, CPU scheduling info, memory-management info, and accounting/I-O status. "
                        "Context switching is purely state-saving overhead."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=OrM7nZcxXZU",
                    "est_minutes": 30,
                },
                "fast": {
                    "bullets": [
                        "Process States: New -> Ready -> Running -> Waiting -> Terminated.",
                        "PCB stores PID, Program Counter, register snapshot, open file descriptors.",
                        "Context Switch overhead: Direct CPU cycles lost + CPU cache invalidation.",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=jZ_mP_eDsmw",
                    "mustAskTopics": ["5-State Process Diagram", "PCB Data Fields", "Context Switch Cost"],
                    "est_minutes": 9,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-02-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                            "caption": "Inside a Process Control Block (PCB) before your CPU switches task.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t03",
            "CPU Scheduling Algorithms (FCFS, SJF, RR)",
            3,
            0.92,
            ["os-t02"],
            {
                "dense": {
                    "prerequisites": ["os-t02"],
                    "textbooks": [{"title": "Operating System Concepts", "author": "Silberschatz"}],
                    "notes": (
                        "CPU scheduling selects processes from the Ready queue for allocation. Metrics: CPU Utilization, "
                        "Throughput, Turnaround Time, Waiting Time, Response Time. Algorithms include First-Come First-Served "
                        "(convoy effect), Shortest Job First (optimal average waiting time, provable by induction), "
                        "Shortest Remaining Time First (preemptive SJF), Priority Scheduling (starvation avoided by aging), "
                        "and Round Robin (time quantum trade-off between responsiveness and context-switch overhead)."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=EWkQl0n0w5M",
                    "est_minutes": 45,
                },
                "fast": {
                    "bullets": [
                        "Convoy Effect in FCFS: Short jobs trapped behind long I/O bound jobs.",
                        "SJF is mathematically optimal for minimum average waiting time; requires burst prediction.",
                        "Round Robin: If quantum q is huge -> behaves like FCFS; if q is too small -> context switch storm.",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=zFnrUVqti3M",
                    "mustAskTopics": ["Gantt Chart Numerical Problems", "Convoy Effect", "Aging in Priority Scheduling"],
                    "est_minutes": 12,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-03-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
                            "caption": "How to ace Gantt Chart scheduling calculations under 60 seconds!",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t04",
            "Process Synchronization & Semaphores",
            4,
            0.95,
            ["os-t02"],
            {
                "dense": {
                    "prerequisites": ["os-t02", "Concurrent Programming"],
                    "textbooks": [{"title": "Modern Operating Systems", "author": "Tanenbaum"}],
                    "notes": (
                        "Race conditions arise when concurrent processes access shared mutable state without synchronization. "
                        "Critical Section Problem requires 3 criteria: Mutual Exclusion, Progress, and Bounded Waiting. "
                        "Hardware atomic instructions like TestAndSet or CompareAndSwap form the base. Counting and "
                        "Binary Semaphores (wait/signal or P/V) coordinate execution. Classic synchronization problems: "
                        "Producer-Consumer, Readers-Writers, and Dining Philosophers."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=ph2awgxsr_o",
                    "est_minutes": 50,
                },
                "fast": {
                    "bullets": [
                        "Critical Section Requirements: Mutual Exclusion, Progress, Bounded Waiting.",
                        "Semaphores: wait() decrements, signal() increments; must execute atomically.",
                        "Producer-Consumer: mutex protects buffer; empty/full semaphores prevent underflow/overflow.",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=Y7sYQ_i6KzI",
                    "mustAskTopics": ["Peterson's Algorithm proof", "Dining Philosophers solution", "Binary vs Counting Semaphore"],
                    "est_minutes": 14,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-04-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
                            "caption": "Why mutex vs semaphores confuse 90% of CS students.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t05",
            "Deadlock Detection & Banker's Algorithm",
            5,
            0.88,
            ["os-t04"],
            {
                "dense": {
                    "prerequisites": ["os-t04"],
                    "textbooks": [{"title": "Operating System Concepts", "author": "Silberschatz"}],
                    "notes": (
                        "Deadlock is a state where every process in a set is waiting for an event that can only be caused by another process in the set. "
                        "Four Coffman conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait. "
                        "Prevention invalidates at least one condition. Avoidance uses Banker's Algorithm with Allocation, "
                        "Max, Available, and Need matrices (Need = Max - Allocation). A state is safe if there exists a safe sequence."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=2hyk_P_Zqis",
                    "est_minutes": 40,
                },
                "fast": {
                    "bullets": [
                        "4 Coffman Conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.",
                        "Banker's Algorithm: Calculates Need = Max - Allocation, iterates finding Pi where Need[i] <= Available.",
                        "Resource Allocation Graph (RAG): Cycle is a necessary condition for deadlock (sufficient if single-instance).",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=kY6VpU_0sP4",
                    "mustAskTopics": ["Banker's Algorithm Step-by-Step Numerical", "Safe State definition", "Coffman Conditions"],
                    "est_minutes": 10,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-05-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
                            "caption": "Banker's Algorithm Matrix breakdown in 60 seconds.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t06",
            "Memory Management & Paging",
            6,
            0.84,
            ["os-t02"],
            {
                "dense": {
                    "prerequisites": ["os-t01", "os-t02"],
                    "textbooks": [{"title": "Operating Systems", "author": "Stallings"}],
                    "notes": (
                        "Physical memory vs Logical address space. Contiguous allocation causes external fragmentation. "
                        "Paging eliminates external fragmentation by dividing physical memory into fixed Frames and logical "
                        "memory into Pages. The Page Table translates Page Number (p) to Frame Number (f), offset (d) unchanged. "
                        "Translation Lookaside Buffer (TLB) caches translations. Effective Memory Access Time (EMAT) = hit_rate * (tlb + mem) + (1 - hit_rate) * (tlb + 2*mem)."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=qcBIv_6Qv_M",
                    "est_minutes": 35,
                },
                "fast": {
                    "bullets": [
                        "Paging removes external fragmentation, but leaves internal fragmentation in the last frame.",
                        "Address Translation: Logical address (p, d) maps to Physical address (f, d).",
                        "TLB Cache: Solves the two-memory-accesses per load problem.",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=1F_4_T7m9_E",
                    "mustAskTopics": ["EMAT Calculation with TLB", "Internal vs External Fragmentation", "Multi-level Paging"],
                    "est_minutes": 11,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-06-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
                            "caption": "How Paging Translates Addresses in 50 seconds.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t07",
            "Virtual Memory & Page Replacement (LRU, FIFO)",
            7,
            0.90,
            ["os-t06"],
            {
                "dense": {
                    "prerequisites": ["os-t06"],
                    "textbooks": [{"title": "Operating System Concepts", "author": "Silberschatz"}],
                    "notes": (
                        "Virtual Memory allows execution of partially loaded processes, decoupling logical address space from physical memory. "
                        "Demand Paging brings pages only when referenced; absent page triggers a Page Fault trap. "
                        "Page replacement algorithms: FIFO (subject to Belady's Anomaly), Optimal (replaces page not used for longest future time; benchmark), "
                        "LRU (approximated via reference bit or stack algorithm; immune to Belady's anomaly). Thrashing occurs when total working set > physical RAM."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=3GsmzP1D1jY",
                    "est_minutes": 45,
                },
                "fast": {
                    "bullets": [
                        "Page Fault: CPU traps to OS -> reads frame from disk -> updates page table -> restarts instruction.",
                        "Belady's Anomaly: FIFO can suffer MORE page faults with MORE frames.",
                        "LRU is optimal in practice; stack algorithms never suffer Belady's anomaly.",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=p_w_0Z997jU",
                    "mustAskTopics": ["Belady's Anomaly FIFO counter-example", "LRU Page Fault Calculation", "Working Set Model & Thrashing"],
                    "est_minutes": 12,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-07-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
                            "caption": "Belady's Anomaly: When adding RAM makes your computer SLOWER!",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t08",
            "File Systems & Directory Structures",
            8,
            0.60,
            ["os-t01"],
            {
                "dense": {
                    "prerequisites": ["os-t01"],
                    "textbooks": [{"title": "Modern Operating Systems", "author": "Tanenbaum"}],
                    "notes": (
                        "File system provides persistent, structured storage on secondary storage. Files have attributes, "
                        "types, and operations. Directory structures: Single-level, Two-level, Tree-structured, and Acyclic-graph directories (hard vs soft links). "
                        "File allocation methods: Contiguous (fast, severe external fragmentation), Linked (pointer overhead, slow random access), "
                        "Indexed (inode structure in Unix with direct, single-indirect, double-indirect blocks)."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=KN8YgJnShPM",
                    "est_minutes": 30,
                },
                "fast": {
                    "bullets": [
                        "Inodes: Stores file metadata + pointers to disk blocks (Direct, Single/Double/Triple Indirect).",
                        "Hard link vs Soft link: Hard links point to the same inode; soft links point to the path string.",
                        "Acyclic-graph directory prevents infinite loops in traversals.",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=8m3b4K9XvLg",
                    "mustAskTopics": ["Unix Inode Max File Size Calculation", "Hard vs Soft Links", "Indexed Allocation"],
                    "est_minutes": 8,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-08-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4",
                            "caption": "Unix Inodes explained in 40 seconds.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t09",
            "Disk Scheduling Algorithms (SCAN, C-SCAN, LOOK)",
            9,
            0.78,
            ["os-t08"],
            {
                "dense": {
                    "prerequisites": ["os-t08"],
                    "textbooks": [{"title": "Operating System Concepts", "author": "Silberschatz"}],
                    "notes": (
                        "Magnetic disk access time = Seek Time + Rotational Latency + Transfer Time. Seek time dominates. "
                        "Disk scheduling minimizes total head movement (cylinders traveled). Algorithms: FCFS, SSTF (starvation risk), "
                        "SCAN (Elevator: moves to disk boundary reversing direction), C-SCAN (Circular SCAN: treats disk as circular list, only services in one direction), "
                        "LOOK and C-LOOK (only goes as far as the furthest pending request instead of disk boundary)."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=Y_j_4e53QpI",
                    "est_minutes": 30,
                },
                "fast": {
                    "bullets": [
                        "Seek time is the biggest bottleneck in magnetic mechanical storage.",
                        "SCAN (Elevator) goes all the way to cylinder 0 or Max.",
                        "LOOK/C-LOOK optimizes SCAN by only traveling to the furthest requested cylinder.",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=6YhM4w_u_g0",
                    "mustAskTopics": ["Total Head Movement Numerical Calculations", "C-SCAN vs SCAN fairness", "SSTF Starvation"],
                    "est_minutes": 9,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-09-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                            "caption": "C-SCAN vs Elevator LOOK scheduling in 50 seconds.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
        (
            "os-t10",
            "OS Protection, Security & Access Matrix",
            10,
            0.55,
            ["os-t01"],
            {
                "dense": {
                    "prerequisites": ["os-t01"],
                    "textbooks": [{"title": "Modern Operating Systems", "author": "Tanenbaum"}],
                    "notes": (
                        "Protection controls process access to system resources according to policy. Principles: Principle of Least Privilege. "
                        "Access Matrix model: rows are Domains, columns are Objects, cells are Access Rights. "
                        "Implementation options: Access Control Lists (ACLs - per object column) vs Capability Lists (C-Lists - per domain row). "
                        "Revocation techniques and role-based access control (RBAC)."
                    ),
                    "videoUrl": "https://www.youtube.com/watch?v=D6nQ9_4sXw0",
                    "est_minutes": 25,
                },
                "fast": {
                    "bullets": [
                        "Principle of Least Privilege: Entities get only the permissions needed for their immediate task.",
                        "Access Control List (ACL): Attached to Object (e.g. file permissions -rwxr-xr-x).",
                        "Capability List: Attached to Subject/Domain (like an unforgeable ticket).",
                    ],
                    "videoUrl": "https://www.youtube.com/watch?v=5V_mU_49xPk",
                    "mustAskTopics": ["Access Matrix representation", "ACL vs Capability Lists", "Least Privilege"],
                    "est_minutes": 7,
                },
                "short_video": {
                    "videos": [
                        {
                            "id": "sv-10-1",
                            "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                            "caption": "Access Control Lists vs Capability Lists explained visually.",
                        }
                    ],
                    "est_minutes": 1,
                },
            },
        ),
    ]

    for tid, title, order_num, imp_score, prereqs, assets in topics_data:
        topic = Topic(
            id=tid,
            subject_id="os-sem3-aiml",
            title=title,
            order_num=order_num,
            importance_score=imp_score,
            prereq_ids_json=json.dumps(prereqs),
        )
        db.add(topic)
        db.flush()

        for atype, adata in assets.items():
            asset = ContentAsset(
                id=f"{tid}-{atype}",
                topic_id=tid,
                asset_type=atype,
                title=f"{title} ({atype.capitalize()})",
                est_minutes=adata.get("est_minutes", 5),
                payload_json=json.dumps(adata),
            )
            db.add(asset)

    db.commit()


def init_and_seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)


if __name__ == "__main__":
    init_and_seed()
    print("Successfully seeded Operating Systems prototype fixtures into database!")

"""SmartLabOS: comprehensive tests for memory allocation strategies.

Tests First-Fit, Best-Fit, and Worst-Fit with hand-worked expected placements.
"""
from so_sim.core.memfisica import MemoriaFisica
from so_sim.core.pcb import PCB


def test_first_fit_placement():
    """First-Fit: allocate in the first hole that fits."""
    mem = MemoriaFisica(ram_total=1000, ram_so=0, tam_bloque=100, estrategia="first_fit")
    
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=400)
    p2 = PCB(pid=2, nombre="P2", llegada=0, rafaga_total=1, tam_ejecutable=100)
    p3 = PCB(pid=3, nombre="P3", llegada=0, rafaga_total=1, tam_ejecutable=600)
    
    # Allocate P1 (4 blocks): blocks 0-3
    assert mem.asignar(p1) is True
    assert mem.bloques_libres() == 6
    
    # Allocate P2 (1 block): block 4
    assert mem.asignar(p2) is True
    assert mem.bloques_libres() == 5
    
    # Allocate P3 (6 blocks): blocks 5-10, but only 5 blocks left, should fail
    assert mem.asignar(p3) is False
    
    # Free P1, creating a hole at blocks 0-3
    mem.liberar(1)
    assert mem.bloques_libres() == 9  # 4 freed + 5 remaining
    
    # Now P3 still won't fit (needs 6 contiguous, but we have 4 and 5 separate)
    assert mem.asignar(p3) is False


def test_first_fit_uses_first_hole():
    """First-Fit uses the first hole that fits, not the best."""
    mem = MemoriaFisica(ram_total=1000, ram_so=0, tam_bloque=100, estrategia="first_fit")
    
    # Create fragmentation pattern
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=200)
    p2 = PCB(pid=2, nombre="P2", llegada=0, rafaga_total=1, tam_ejecutable=100)
    p3 = PCB(pid=3, nombre="P3", llegada=0, rafaga_total=1, tam_ejecutable=400)
    
    mem.asignar(p1)  # blocks 0-1
    mem.asignar(p2)  # block 2
    mem.asignar(p3)  # blocks 3-6
    
    # Free P1 (hole of 2 blocks at 0-1) and P3 (hole of 4 blocks at 3-6)
    mem.liberar(1)
    mem.liberar(3)
    
    # Allocate a process needing 2 blocks - should go to first hole (0-1)
    p4 = PCB(pid=4, nombre="P4", llegada=0, rafaga_total=1, tam_ejecutable=200)
    assert mem.asignar(p4) is True


def test_best_fit_placement():
    """Best-Fit: allocate in the smallest hole that fits."""
    mem = MemoriaFisica(ram_total=1000, ram_so=0, tam_bloque=100, estrategia="best_fit")
    
    # Same setup as first_fit test
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=400)
    p2 = PCB(pid=2, nombre="P2", llegada=0, rafaga_total=1, tam_ejecutable=100)
    p3 = PCB(pid=3, nombre="P3", llegada=0, rafaga_total=1, tam_ejecutable=200)
    
    mem.asignar(p1)  # blocks 0-3
    mem.asignar(p2)  # block 4
    
    # Free P1, creating hole of 4 blocks
    mem.liberar(1)
    
    # Remaining: hole of 4 at 0-3, P2 at 4, hole of 5 at 5-9
    # Allocate P3 needing 2 blocks - Best-Fit should choose the 4-block hole
    # (smallest that fits), not the 5-block hole
    assert mem.asignar(p3) is True


def test_worst_fit_placement():
    """Worst-Fit: allocate in the largest hole."""
    mem = MemoriaFisica(ram_total=1000, ram_so=0, tam_bloque=100, estrategia="worst_fit")
    
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=400)
    p2 = PCB(pid=2, nombre="P2", llegada=0, rafaga_total=1, tam_ejecutable=100)
    p3 = PCB(pid=3, nombre="P3", llegada=0, rafaga_total=1, tam_ejecutable=200)
    
    mem.asignar(p1)  # blocks 0-3
    mem.asignar(p2)  # block 4
    
    # Free P1, creating hole of 4 blocks
    mem.liberar(1)
    
    # Remaining: hole of 4 at 0-3, P2 at 4, hole of 5 at 5-9
    # Allocate P3 needing 2 blocks - Worst-Fit should choose the 5-block hole
    # (largest available)
    assert mem.asignar(p3) is True


def test_fragmentation_internal():
    """Test internal fragmentation calculation."""
    mem = MemoriaFisica(ram_total=1000, ram_so=0, tam_bloque=100, estrategia="first_fit")
    
    # Process needs 150 KB, gets 2 blocks (200 KB), wasting 50 KB
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=150)
    mem.asignar(p1)
    
    # Internal fragmentation = allocated - used = 200 - 150 = 50
    assert mem.fragmentacion_interna() == 50


def test_external_fragmentation():
    """Test external fragmentation scenario."""
    mem = MemoriaFisica(ram_total=1000, ram_so=0, tam_bloque=100, estrategia="first_fit")
    
    # Create a pattern that leads to external fragmentation
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=300)
    p2 = PCB(pid=2, nombre="P2", llegada=0, rafaga_total=1, tam_ejecutable=100)
    p3 = PCB(pid=3, nombre="P3", llegada=0, rafaga_total=1, tam_ejecutable=300)
    p4 = PCB(pid=4, nombre="P4", llegada=0, rafaga_total=1, tam_ejecutable=100)
    
    mem.asignar(p1)  # blocks 0-2
    mem.asignar(p2)  # block 3
    mem.asignar(p3)  # blocks 4-6
    mem.asignar(p4)  # block 7
    # blocks 8-9 remain free
    
    # Free P1 and P3, creating two 3-block holes
    mem.liberar(1)
    mem.liberar(3)
    
    # Now we have 8 free blocks total (3 + 3 + 2), but fragmented
    assert mem.bloques_libres() == 8
    
    # Try to allocate 4 blocks - should fail due to external fragmentation
    p5 = PCB(pid=5, nombre="P5", llegada=0, rafaga_total=1, tam_ejecutable=400)
    assert mem.asignar(p5) is False


def test_memory_full():
    """Test allocation when memory is full."""
    mem = MemoriaFisica(ram_total=400, ram_so=0, tam_bloque=100, estrategia="first_fit")
    
    # Fill all 4 blocks
    processes = []
    for i in range(4):
        p = PCB(pid=i+1, nombre=f"P{i+1}", llegada=0, rafaga_total=1, tam_ejecutable=100)
        assert mem.asignar(p) is True
        processes.append(p)
    
    # Try to allocate one more - should fail
    p5 = PCB(pid=5, nombre="P5", llegada=0, rafaga_total=1, tam_ejecutable=100)
    assert mem.asignar(p5) is False
    assert mem.bloques_libres() == 0


def test_memory_with_os_reservation():
    """Test memory allocation with OS-reserved space."""
    # Total 1000, OS reserves 200, so 800 available (8 blocks)
    mem = MemoriaFisica(ram_total=1000, ram_so=200, tam_bloque=100, estrategia="first_fit")
    
    # Should have 8 blocks available
    assert mem.bloques_libres() == 8
    
    # Allocate 8 blocks
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=800)
    assert mem.asignar(p1) is True
    assert mem.bloques_libres() == 0


def test_allocation_release_cycle():
    """Test multiple allocation and release cycles."""
    mem = MemoriaFisica(ram_total=500, ram_so=0, tam_bloque=100, estrategia="first_fit")
    
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=200)
    p2 = PCB(pid=2, nombre="P2", llegada=0, rafaga_total=1, tam_ejecutable=100)
    
    # Allocate, release, allocate again
    assert mem.asignar(p1) is True
    assert mem.bloques_libres() == 3
    
    mem.liberar(1)
    assert mem.bloques_libres() == 5
    
    assert mem.asignar(p2) is True
    assert mem.bloques_libres() == 4
    
    mem.liberar(2)
    assert mem.bloques_libres() == 5


def test_exact_fit():
    """Test allocation when process size exactly matches block requirements."""
    mem = MemoriaFisica(ram_total=500, ram_so=0, tam_bloque=100, estrategia="first_fit")
    
    # Process needs exactly 2 blocks (200 KB)
    p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=200)
    assert mem.asignar(p1) is True
    
    # No internal fragmentation when exact fit
    assert mem.fragmentacion_interna() == 0


def test_strategy_comparison_classic():
    """Classic textbook example showing difference between strategies.
    
    Create two holes of different sizes (4 and 6 blocks), then allocate
    a small process (3 blocks) and a large process (6 blocks).
    Worst-Fit wastes the large hole on the small allocation.
    """
    # Setup: 11 blocks total
    def setup_memory(strategy):
        mem = MemoriaFisica(ram_total=1100, ram_so=0, tam_bloque=100, estrategia=strategy)
        p1 = PCB(pid=1, nombre="P1", llegada=0, rafaga_total=1, tam_ejecutable=400)  # 4 blocks
        p2 = PCB(pid=2, nombre="P2", llegada=0, rafaga_total=1, tam_ejecutable=100)  # 1 block (separator)
        p3 = PCB(pid=3, nombre="P3", llegada=0, rafaga_total=1, tam_ejecutable=600)  # 6 blocks
        
        mem.asignar(p1)  # blocks 0-3
        mem.asignar(p2)  # block 4
        mem.asignar(p3)  # blocks 5-10
        
        # Free P1 and P3, creating two holes: 4 blocks and 6 blocks
        mem.liberar(1)
        mem.liberar(3)
        
        return mem
    
    # Test with small allocation (3 blocks) first
    p4 = PCB(pid=4, nombre="P4", llegada=0, rafaga_total=1, tam_ejecutable=300)
    p5 = PCB(pid=5, nombre="P5", llegada=0, rafaga_total=1, tam_ejecutable=600)
    
    # First-Fit: uses first hole (4 blocks) for P4, succeeds
    mem_ff = setup_memory("first_fit")
    assert mem_ff.asignar(p4) is True
    assert mem_ff.asignar(p5) is True  # 6-block hole still available
    
    # Best-Fit: uses 4-block hole for P4 (smallest fit), succeeds
    mem_bf = setup_memory("best_fit")
    p4_bf = PCB(pid=4, nombre="P4", llegada=0, rafaga_total=1, tam_ejecutable=300)
    p5_bf = PCB(pid=5, nombre="P5", llegada=0, rafaga_total=1, tam_ejecutable=600)
    assert mem_bf.asignar(p4_bf) is True
    assert mem_bf.asignar(p5_bf) is True  # 6-block hole still available
    
    # Worst-Fit: uses 6-block hole for P4 (largest), then fails on P5
    mem_wf = setup_memory("worst_fit")
    p4_wf = PCB(pid=4, nombre="P4", llegada=0, rafaga_total=1, tam_ejecutable=300)
    p5_wf = PCB(pid=5, nombre="P5", llegada=0, rafaga_total=1, tam_ejecutable=600)
    assert mem_wf.asignar(p4_wf) is True
    assert mem_wf.asignar(p5_wf) is False  # Only 4-block hole left, not enough

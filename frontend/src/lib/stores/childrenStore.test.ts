import {
	children,
	ChildrenStore,
	type ChildObject,
	type ObservationData
} from '$lib/stores/childrenStore';
import { describe, expect, it } from 'vitest';

describe('normal functionality', () => {
	const mockObservationData: ObservationData = {
		id: 'child1',
		user: 'alpha',
		current: ['a', 'b', 'c'],
		summary: ['x', 'y']
	};
	const mockObservationData2: ObservationData = {
		id: 'child1',
		user: 'beta',
		current: ['a', 'b', 'c'],
		summary: ['x', 'y']
	};
	const mockChildData: ChildObject = {
		childData: {
			id: 'childfoo',
			user: 'alpha',
			name: 'foo',
			age: 3,
			nationality: 'turkish'
		},
		observationData: mockObservationData
	};
	const mockChildData2: ChildObject = {
		childData: {
			id: 'childbar',
			user: 'alpha',
			name: 'bar',
			age: 5,
			nationality: 'german'
		},
		observationData: mockObservationData
	};

	const mockChildData3: ChildObject = {
		childData: {
			id: 'childbaz',
			user: 'beta',
			name: 'baz',
			age: 2,
			nationality: 'british'
		},
		observationData: mockObservationData2
	};

	function reset() {
		children.set({
			alpha: {
				childfoo: mockChildData,
				childbar: mockChildData2
			},
			beta: {
				childfoo: mockChildData3
			}
		});
	}

	it('test singleton pattern', () => {
		try {
			const other = new ChildrenStore();
		} catch (error) {
			expect(error.message).toEqual('Singleton classes cannot be instantiated more than once.');
		}
	});

	it('should add child successfully', async () => {
		reset();
		await children.addChildData('alpha', 'childC', mockChildData3.childData);
		expect(children.get()['alpha']['childC'].childData).toEqual(mockChildData3.childData);
	});

	it('should add child observationdata successfully', async () => {
		reset();

		await children.addChildData('alpha', 'childC', mockChildData3.childData);
		await children.addChildObservation('alpha', 'childC', mockChildData3.observationData);

		expect(children.get()['alpha']['childC'].observationData).toEqual(
			mockChildData3.observationData
		);
	});

	it('cannot assign observationdata when childData is missing', async () => {
		reset();
		try {
			await children.addChildObservation('alpha', 'childC', mockChildData3.observationData);
		} catch (error) {
			expect((error as Error).message).toBe(
				'Child token childC does not exist for user token alpha'
			);
		}
	});

	it('cannot assign observationdata for unknown user', async () => {
		reset();
		try {
			await children.addChildObservation('x', 'childC', mockChildData3.observationData);
		} catch (error) {
			expect((error as Error).message).toBe('User token x not found');
		}
	});

	it('should remove child successfully', async () => {
		reset();
		await children.removeChildData('beta', 'childfoo');
		expect(children.get()['beta']['childfoo']).toEqual(undefined);
	});

	it('should throw when adding with nonexistant user or existing child key', async () => {
		reset();
		try {
			await children.addChildData('alpha', 'childA', mockChildData3.childData);
		} catch (error) {
			expect((error as Error).message).toBe(
				'Child token childA already exists for user token alpha'
			);
		}

		try {
			await children.addChildData('x', 'childA', mockChildData3.childData);
		} catch (error) {
			expect((error as Error).message).toBe('User token x not found');
		}
	});

	it('should throw when removing with nonexistant user or nonexisting child key', async () => {
		reset();
		try {
			await children.removeChildData('x', 'childA');
		} catch (error) {
			expect((error as Error).message).toBe('User token x not found');
		}

		try {
			await children.removeChildData('alpha', 'notthere');
		} catch (error) {
			expect((error as Error).message).toBe('Child token notthere not found for user token alpha');
		}
	});

	it('should fetch observation data', async () => {
		reset();
		expect(await children.fetchObservationData('alpha', 'childfoo')).toEqual(mockObservationData);
	});

	it('should fetch child data', async () => {
		reset();
		expect(await children.fetchChildData('alpha', 'childfoo')).toEqual({
			name: 'foo',
			age: 3,
			nationality: 'turkish',
			id: 'childfoo',
			user: 'alpha'
		});
	});

	it('cannot fetch from unknown keys', async () => {
		reset();

		try {
			await children.fetchObservationData('x', 'childA');
		} catch (error) {
			expect((error as Error).message).toBe('No such user in the childrenstore');
		}

		try {
			await children.fetchObservationData('alpha', 'unknown');
		} catch (error) {
			expect((error as Error).message).toBe('No such child in the childrenstore for user alpha');
		}
	});

	it('should fetch list of childrendata', async () => {
		reset();
		const data = await children.fetchChildrenDataforUser('alpha');

		expect(data).toEqual([mockChildData2.childData, mockChildData.childData]);
	});

	it('should fetch list of observationdata successfully', async () => {
		reset();
		const data = await children.fetchObservationDataForUser('alpha');

		expect(data).toEqual([
			['childfoo', mockObservationData],
			['childbar', mockObservationData]
		]);
	});

	it('cannot fetch childrendata from uknown', async () => {
		reset();

		try {
			await children.fetchChildrenDataforUser('x');
		} catch (error) {
			expect((error as Error).message).toBe('No such user in the childrenstore');
		}
	});

	it('cannot fetch observationdata from uknown', async () => {
		reset();

		try {
			await children.fetchObservationDataForUser('x');
		} catch (error) {
			expect((error as Error).message).toBe('No such user in the childrenstore');
		}
	});
});

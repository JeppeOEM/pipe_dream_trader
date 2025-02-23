import { useState } from 'react'
import { Button } from '../ui/buttons/button';
import { isFloat, addDecimal } from '@/lib/utils/numeric-utils';
import { useUpdateIndicator } from '@/lib/hooks/react-query/useUpdateIndicator';
import { useDeleteIndicator } from '@/lib/hooks/react-query/useDeleteIndicator';
import useStrategyStore from '@/lib/hooks/stores/useStrategyStore';
import { SquareX, InfoIcon } from 'lucide-react';
import Modal from '../ui/modal';

interface GenericIndicatorProps {
	indicatorId: number,
	indicatorName: string,
	settings: Record<string, any>;
	settingsSchema: Record<string, any>;
	dataframeColumn: string;
}

export default function GenericIndicator({ indicatorName, dataframeColumn, indicatorId, settingsSchema, settings }: GenericIndicatorProps) {
	const [formData, setFormData] = useState<Record<string, any>>(settings);
	const [errors, setErrors] = useState<Record<string, string>>({});
	const { strategyId } = useStrategyStore();
	const { mutateAsync: updateIndicator } = useUpdateIndicator(strategyId);
	const { mutateAsync: deleteIndicatorMutation } = useDeleteIndicator(strategyId);

	function handleDelete(id: number) {
		deleteIndicatorMutation(id);
	}

	function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
		setFormData((prevFormData) => ({
			...prevFormData,
			[e.target.name]: e.target.value,
		}));

	}

	const [isModalOpen, setIsModalOpen] = useState(false);

	function toggleModal() {
		setIsModalOpen((prev) => !prev);
	}
	// Validate the inputs on submit
	function handleSubmit(e: React.FormEvent) {
		e.preventDefault();
		const convertedFormData = Object.entries(formData).reduce(
			(acc, [key, value]) => {
				const property = settingsSchema.properties[key];

				if (property) {
					if (property.type === 'integer') {
						const convertedValue = parseInt(value, 10);
						if (isNaN(convertedValue)) {
							acc.errors[key] = `${property.title || key} should be a valid integer`;
						} else {
							acc[key] = convertedValue;
						}
					} else if (property.type === 'number') {
						const convertedValue = parseFloat(value);
						if (!isFloat(value) && isFloat(convertedValue)) {
							acc.errors[key] = `${property.title || key} trimming value into a float`;
						}
						else if (isNaN(convertedValue)) {
							acc.errors[key] = `${property.title || key} should be a valid float`;
						} else {
							acc[key] = convertedValue;
						}
					} else if (property.type === 'boolean') {
						acc[key] = value === 'on';
					} else {
						acc[key] = value;
					}
				} else {
					acc[key] = value;
				}

				return acc;
			},
			{ errors: {} } as { [key: string]: any; errors: Record<string, string> }
		);

		if (Object.keys(convertedFormData.errors).length > 0) {
			setErrors(convertedFormData.errors);
		} else {
			setErrors({});
			const { errors, ...formDataWithoutErrors } = convertedFormData;
			updateIndicator({ indicatorId, settings: formDataWithoutErrors });
		}
	}

	function renderInputField(key: string, property: Record<string, any>) {
		const { default: defaultValue, title, type } = property;
		const excludedKeys = ['kind', 'name', 'ddof', 'talib', 'presma'];
		if (excludedKeys.includes(key)) {
			return null;
		}
		switch (type) {
			case 'string':
				return (
					<div className="mb-2">
						<label htmlFor={key} className="block font-bold mb-1">
							{title || key}:
						</label>
						<input
							id={key}
							name={key}
							value={formData[key]}
							onChange={handleInputChange}
							className="indicator-input"
						/>
						{errors[key] && <span className="text-error">{errors[key]}</span>}
					</div>
				);
			case 'integer':
				return (
					<div className="mb-2">
						<label htmlFor={key} className="block font-bold mb-1">
							{title || key}:
						</label>
						<input
							id={key}
							name={key}
							value={formData[key]}
							onChange={handleInputChange}
							className="indicator-input"
						/>
						{errors[key] && <span className="text-error">{errors[key]}</span>}
					</div>
				);
			case 'number':
				return (
					<div className="mb-2">
						<label htmlFor={key} className="block font-bold mb-1">
							{title || key}:
						</label>
						<input
							id={key}
							name={key}
							value={addDecimal(formData[key] || defaultValue)}
							onChange={handleInputChange}
							className="indicator-input"
						/>
						{errors[key] && <span className="text-error">{errors[key]}</span>}
					</div>
				);
			case 'boolean':
				return (
					<div className="mb-2">
						<label htmlFor={key} className="block font-bold mb-1">
							{title || key}:
						</label>
						<input
							type="checkbox"
							id={key}
							name={key}
							checked={formData[key] || defaultValue}
							onChange={handleInputChange}
							className="indicator-input"
						/>
						{errors[key] && <span className="text-error">{errors[key]}</span>}
					</div>
				);
			default:
				return (
					<div className="mb-2">
						<label htmlFor={key} className="block font-bold mb-1">
							{title || key}:
						</label>
						<input
							type="text"
							id={key}
							name={key}
							value={formData[key] || defaultValue || ''}
							onChange={handleInputChange}
							className="indicator-input"
						/>
						{errors[key] && <span className="text-error">{errors[key]}</span>}
					</div>
				);
		}
	}

	return (
		<div className='flex flex-col border rounded-lg p-4 custom-white'>
			<Modal onClose={toggleModal} isOpen={isModalOpen} title={`Indicator: ${formData['kind']}`}>
				<section>
					<pre className="whitespace-pre-wrap break-words p-4 rounded-md">
						{settingsSchema.description}
					</pre>
				</section>
			</Modal>
			<div className='flex flex-row justify-between'>
				<button className="mb-4 appearance-none" onClick={() => handleDelete(indicatorId)}>
					<div className="flex items-center space-x-2">
						<span>Delete</span>
						<SquareX />
					</div>
				</button>
			</div>

			<div className='flex flex-row'>
				<h4 className='h4 font-bold mr-2'>{indicatorName}</h4>
				{dataframeColumn && <p className='text-lg mr-2'>{dataframeColumn}</p>}
				<InfoIcon className='cursor-pointer' onClick={toggleModal} />
			</div>
			<hr className='py-1' />
			<form className='flex flex-row justify-between' onSubmit={handleSubmit}>
				<div className='flex flex-col'>
					<div className='flex flex-row space-x-2'>
						{Object.entries(settingsSchema.properties).map(([key, property]) => {
							return (<div key={key}>
								{renderInputField(key, property as Record<string, any>)}
							</div>);
						})}

					</div>

					<Button className='mt-auto ml-3 mb-2' type='submit'> Submit</Button>
				</div>
			</form>
		</div>
	);
}
